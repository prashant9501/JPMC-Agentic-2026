"""agent.py — system prompt, ReAct agent (create_agent) and the call_agent helper.
Every block below is copied from the Lab 2.2 notebook; the source cell number is marked on each block."""
import json, re
# create_agent replaces langgraph.prebuilt.create_react_agent, deprecated in LangGraph 1.x.
from langchain.agents import create_agent  # as per langchain v1.01
from tools import tools


# ======================================================================
# Notebook cell [31] — create the ReAct agent
# ======================================================================
SYSTEM_PROMPT = """You are a senior financial analyst at Meridian Wealth Partners, a SEBI-registered wealth
management firm managing Rs 2,000 Crore in assets across 800 high-net-worth Indian clients.

Your job is to prepare comprehensive client briefings and answer investment queries using your tools.

AVAILABLE DATA SOURCES:
1. portfolio_lookup — queries the SQL database for client holdings, allocation, and risk profile
2. market_data_search — queries the SQL database for stock/sector data (price, YTD, PE, analyst ratings)
3. calculate_metrics — computes financial metrics (returns, allocation percentages, comparisons)
4. policy_retriever — RAG search over the firm's 5 investment policy PDFs (asset allocation, risk management,
   suitability standards, rebalancing protocol, reporting standards)
5. tavily_search — searches the web for latest market news, RBI updates, sector analysis

GUIDELINES:
- Always check the client's risk profile before making recommendations
- When checking policy compliance, ALWAYS use the policy_retriever tool — never guess the rules
- Cite specific policy document names and page numbers when referencing guidelines
- Do not provide compliance conclusions without first using policy_retriever.
- Do not provide market-news claims without using tavily_search.
- If required data is missing, say so explicitly instead of inferring.
- Use Indian Rupee (₹) for all amounts. Use lakhs and crores for large values.
- Include specific numbers: exact returns, allocation percentages, policy thresholds
- For briefings, structure as: Portfolio Summary → Market Context → Policy Compliance → Recommendations
"""

agent = create_agent(
    model="openai:gpt-5-mini",
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)

print("✅ ReAct agent created")
print(f"   LLM: gpt-5-mini (ChatOpenAI)")
print(f"   Tools: {[agent_tool.name for agent_tool in tools]}")
print(f"   Data: SQLite DB + FAISS (from 5 PDFs) + Tavily web search")


# ======================================================================
# Notebook cell [40] — call_agent helper
# ======================================================================
def call_agent(query):
    """Run the agent on `query`, print the answer, and report which tools (web/policy) it used."""
    print(f"📋 Query: {query}")
    print(f"{'='*80}\n")

    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": query}
            ]
        }
    )

    print("\n🤖 AGENT RESPONSE:")
    print(f"{'─'*80}")

    final_message = result["messages"][-1]
    print(final_message.content if hasattr(final_message, "content") else final_message)

    tool_calls = [message for message in result["messages"] if type(message).__name__ == "ToolMessage"]
    print(f"\n📊 Tools used: {[message.name for message in tool_calls]}")

    web_calls = [message for message in result["messages"]
                 if type(message).__name__ == "ToolMessage" and message.name == "tavily_search"]
    print(f"\n🌐 Web search called: {len(web_calls)} time(s)")

    # Verify policy_retriever was used
    policy_calls = [message for message in result["messages"]
                    if type(message).__name__ == "ToolMessage" and message.name == "policy_retriever"]
    print(f"\n📚 Policy retriever called: {len(policy_calls)} time(s)")
    for policy_call in policy_calls:
        pdf_refs = re.findall(r'[A-Za-z_]+\.pdf', policy_call.content)
        if pdf_refs:
            print(f"   Referenced PDFs: {', '.join(set(pdf_refs))}")

    return result