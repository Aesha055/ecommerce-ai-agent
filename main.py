
import os
import asyncio
import threading
import uvicorn
from fastmcp import FastMCP
from fastapi import FastAPI
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

app = FastAPI()

mcp = FastMCP("ecommerce-product-catalog")

products = {
    "P001": {"name": "Nike Air Max", "price": 4999, "stock": 15, "category": "Shoes"},
    "P002": {"name": "Samsung 55 TV", "price": 49999, "stock": 3, "category": "Electronics"},
    "P003": {"name": "Leather Laptop Bag", "price": 1999, "stock": 20, "category": "Accessories"},
    "P004": {"name": "Wireless Earbuds", "price": 2499, "stock": 8, "category": "Electronics"},
}

@mcp.tool()
def search_products(query: str) -> dict:
    results = []
    for pid, p in products.items():
        if query.lower() in p["name"].lower() or query.lower() in p["category"].lower():
            results.append({"id": pid, **p})
    return {"results": results if results else "No products found."}

@mcp.tool()
def get_product_details(product_id: str) -> dict:
    p = products.get(product_id.upper())
    if p:
        return {"product_id": product_id, **p}
    return {"error": f"Product {product_id} not found."}

@mcp.tool()
def check_stock(product_id: str) -> dict:
    p = products.get(product_id.upper())
    if p:
        return {"product_id": product_id, "name": p["name"], "in_stock": p["stock"] > 0, "quantity": p["stock"]}
    return {"error": f"Product {product_id} not found."}

mcp_app = mcp.http_app(transport="sse")
app.mount("/mcp", mcp_app)

@app.get("/")
def home():
    return {"status": "E-commerce AI Agent is running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
