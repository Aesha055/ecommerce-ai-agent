# E-Commerce AI Support Agent

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-8E75F7?style=for-the-badge&logo=google&logoColor=white)
![Google ADK](https://img.shields.io/badge/Google%20ADK-4285F4?style=for-the-badge&logo=google&logoColor=white)

**LLM-powered customer support agent** built using **Google ADK**, **Gemini**, **FastAPI**, and **FastMCP**.

---

## Overview

An intelligent AI customer support assistant that handles e-commerce queries including order tracking, return requests, product search, and inventory checks using **Generative AI** and **tool calling**.

The agent uses **Google ADK** (Agent Development Kit) with the **Gemini** LLM and integrates external tools via **FastMCP** for real-time data retrieval.

---

## Features

- **Order Status Tracking** — Real-time order status updates
- **Return Request Processing** — Handle return and refund requests
- **FAQ Automation** — Answer frequently asked questions on shipping, payment, and cancellations
- **Product Catalog Search** — Search products by keyword or category
- **Inventory Lookup** — Check current stock availability
- **Multi-turn Conversations** — Maintain context throughout the conversation
- **Tool Integration** — Seamless MCP-based tool calling

---

## Tech Stack

| Component          | Technology   |
|--------------------|--------------|
| Language           | Python       |
| LLM                | Gemini       |
| Agent Framework    | Google ADK   |
| Tool Integration   | FastMCP      |
| Backend Framework  | FastAPI      |
| Communication      | REST APIs    |
| Deployment         | Render       |

---

## Architecture

```
User → Gemini Agent (Google ADK) → Tool Calling → FastMCP Services → Product Catalog / Order Database
```

---

## Live Demo

**Backend API:** [https://ecommerce-ai-agent-89mb.onrender.com](https://ecommerce-ai-agent-89mb.onrender.com)

Sample queries to try:
- `"Check status of order ORD001"`
- `"I want to return order ORD002"`
- `"Search for available laptops"`
- `"Check stock for product P002"`

---

## Demo Output

**Order Status Tracking:**
```
User:  What is the status of order ORD001?
Agent: Your order ORD001 for Nike Shoes has been Shipped. Expected delivery: Tomorrow.
```

**Product Search via FastMCP:**
```
User:  Do you have any electronics?
Agent: Yes, we have:
       1. Samsung 55" TV   — ₹49,999 · In Stock (3 units)
       2. Wireless Earbuds — ₹2,499  · In Stock (8 units)
```

**Return Request Processing:**
```
User:  I want to return ORD002, it arrived damaged.
Agent: Return for ORD002 accepted. Reason: damaged. Refund in 5-7 days.
```

**FAQ Automation:**
```
User:  What is your return policy?
Agent: Return within 30 days. Items must be unused and in original condition.
```

**Multi-turn Conversation:**
```
User:  What is the status of order ORD002?
Agent: Your order ORD002 for Samsung TV has been Delivered.
       Since a return was processed, your refund will arrive in 5-7 days.
```

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Aesha055/ecommerce-ai-agent.git
   cd ecommerce-ai-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file and add your Gemini API key:**
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

---

## Repository Structure

```
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md
```

---

## Skills Demonstrated

- LLM Integration with Google Gemini
- Agentic AI Workflows using Google ADK
- Tool Calling and Function Calling
- MCP (Model Context Protocol) Integration
- Multi-turn Conversation Management
- REST API development with FastAPI
- Cloud Deployment on Render

---

## Notes

- Do **not** hardcode API keys in `main.py` — use the `.env` file
- The live backend returns `{"status": "E-commerce AI Agent is running!"}` on the root endpoint
