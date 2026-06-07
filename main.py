import os
import asyncio
import uvicorn
from fastmcp import FastMCP
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# ── ENV ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# ── FASTAPI APP ────────────────────────────────────────────────────────────
app = FastAPI(title="E-Commerce AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DATA ───────────────────────────────────────────────────────────────────
products = {
    "P001": {"name": "Nike Air Max",       "price": 4999,  "stock": 15, "category": "Shoes"},
    "P002": {"name": "Samsung 55 TV",      "price": 49999, "stock": 3,  "category": "Electronics"},
    "P003": {"name": "Leather Laptop Bag", "price": 1999,  "stock": 20, "category": "Accessories"},
    "P004": {"name": "Wireless Earbuds",   "price": 2499,  "stock": 8,  "category": "Electronics"},
}

orders = {
    "ORD001": {"item": "Nike Shoes",  "status": "Shipped",    "eta": "Tomorrow"},
    "ORD002": {"item": "Samsung TV",  "status": "Delivered",  "eta": "Done"},
    "ORD003": {"item": "Laptop Bag",  "status": "Processing", "eta": "3 days"},
}

# ── MCP SERVER ─────────────────────────────────────────────────────────────
mcp = FastMCP("ecommerce-product-catalog")

@mcp.tool()
def search_products(query: str) -> dict:
    """Search for products by name or category."""
    results = [{"id": pid, **p} for pid, p in products.items()
               if query.lower() in p["name"].lower() or query.lower() in p["category"].lower()]
    return {"results": results if results else "No products found."}

@mcp.tool()
def get_product_details(product_id: str) -> dict:
    """Get full details of a product by its ID."""
    p = products.get(product_id.upper())
    return {"product_id": product_id, **p} if p else {"error": f"Product {product_id} not found."}

@mcp.tool()
def check_stock(product_id: str) -> dict:
    """Check if a product is in stock."""
    p = products.get(product_id.upper())
    if p:
        return {"product_id": product_id, "name": p["name"], "in_stock": p["stock"] > 0, "quantity": p["stock"]}
    return {"error": f"Product {product_id} not found."}

@mcp.tool()
def check_order_status(order_id: str) -> dict:
    """Check the status of a customer order by order ID."""
    order = orders.get(order_id.upper())
    return {"status": "success", "order_id": order_id, **order} if order else {"status": "error", "message": f"Order {order_id} not found."}

@mcp.tool()
def process_return_request(order_id: str, reason: str) -> dict:
    """Process a return request for a given order."""
    order = orders.get(order_id.upper())
    if order:
        return {"status": "success", "message": f"Return for {order_id} accepted. Reason: {reason}. Refund in 5-7 days."}
    return {"status": "error", "message": f"Order {order_id} not found."}

@mcp.tool()
def get_faq(topic: str) -> dict:
    """Answer FAQs about shipping, payment, returns, cancellations."""
    faqs = {
        "shipping": "Free shipping above ₹999. Delivery in 3-5 days.",
        "return":   "Return within 30 days. Items must be unused.",
        "payment":  "We accept UPI, cards, net banking, and COD.",
        "cancel":   "Cancel within 24 hours of placing the order.",
    }
    return {"status": "success", "answer": faqs.get(topic.lower(), "Sorry, I don't have info on that topic.")}

# Mount MCP server under /mcp
mcp_app = mcp.http_app(transport="sse")
app.mount("/mcp", mcp_app)

# ── AGENT SETUP ────────────────────────────────────────────────────────────
session_service = InMemorySessionService()
runner = None

@app.on_event("startup")
async def startup():
    global runner
    await asyncio.sleep(1)  # let MCP SSE server settle

    mcp_toolset = MCPToolset(
        connection_params=SseConnectionParams(url="http://127.0.0.1:8000/mcp/sse")
    )

    agent = Agent(
        name="ecommerce_support_agent",
        model="gemini-2.0-flash",
        description="AI customer support agent for an e-commerce store.",
        instruction="""
            You are a friendly customer support agent for an online store called ShopAI.
            Help customers with order status, returns, product search, stock checks, and FAQs.
            Always be polite and concise.
            If you cannot help, say: 'Let me connect you to a human agent.'
        """,
        tools=[mcp_toolset],
    )

    runner = Runner(agent=agent, app_name="ecommerce_agent", session_service=session_service)
    print("✅ Agent initialised and ready!")

# ── MODELS ─────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    reply: str
    session_id: str

# ── /chat ENDPOINT ─────────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Send a message to the AI agent and receive a reply."""
    if runner is None:
        return ChatResponse(reply="Agent is still starting up. Please try again in a moment.", session_id=req.session_id)

    # Create session if not exists
    try:
        await session_service.create_session(
            app_name="ecommerce_agent",
            user_id=req.session_id,
            session_id=req.session_id,
        )
    except Exception:
        pass  # already exists

    content = types.Content(role="user", parts=[types.Part(text=req.message)])
    reply_text = "Sorry, I couldn't process that. Please try again."

    async for event in runner.run_async(user_id=req.session_id, session_id=req.session_id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            reply_text = event.content.parts[0].text
            break

    return ChatResponse(reply=reply_text, session_id=req.session_id)

# ── ROOT ───────────────────────────────────────────────────────────────────
@app.get("/")
def home():
    return {
        "status": "E-Commerce AI Agent is running!",
        "chat_endpoint": "POST /chat",
        "docs": "/docs"
    }

# ── ENTRY POINT ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
