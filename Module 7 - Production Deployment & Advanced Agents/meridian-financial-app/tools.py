"""tools.py — keys, clients, data paths, FAISS RAG pipeline, DB helpers and the 5 agent tools.
Every block below is copied from the Lab 2.2 notebook; the source cell number is marked on each block."""


# ======================================================================
# Notebook cell [6] — API key configuration
# ======================================================================
import os, json, sqlite3, textwrap, re

# Where to get each key. Your instructor supplies the keys for this course; add each one to
# the course's .env file as KEY_NAME=value.
KEY_SIGNUP_PAGES = {
    "OPENAI_API_KEY": "supplied by your instructor (elsewhere: https://platform.openai.com/api-keys)",
    "TAVILY_API_KEY": "https://app.tavily.com (free tier)",
    "GROQ_API_KEY": "https://console.groq.com/keys (free tier)",
    "WEATHER_API_KEY": "https://www.weatherapi.com/signup.aspx (free tier)",
    "LANGSMITH_API_KEY": "https://smith.langchain.com -> Settings -> API Keys (free tier)",
    "ANTHROPIC_API_KEY": "https://console.anthropic.com/settings/keys",
    "GEMINI_API_KEY": "https://aistudio.google.com/app/apikey",
}


def load_keys(required):
    """Load API keys from Colab Secrets (on Colab) or a local .env file (elsewhere).

    Prints one line per key, then stops with instructions if a required key is missing.

    Args:
        required: the environment-variable names this lab needs.
    """
    try:
        from google.colab import userdata          # running on Google Colab
        for key_name in required:
            try:
                os.environ[key_name] = userdata.get(key_name)
            except Exception:
                pass                                 # not set in Colab Secrets
        source = "Colab Secrets"
    except ImportError:                              # the training VM, or any local machine
        from dotenv import find_dotenv, load_dotenv
        load_dotenv(find_dotenv(usecwd=True))        # searches upward for the course's .env file
        source = ".env / environment"
    print(f"\U0001F511 Key source: {source}")
    for key_name in required:
        print(f"   {key_name:<22} {'✅' if os.environ.get(key_name) else '❌ MISSING'}")
    missing_keys = [key_name for key_name in required if not os.environ.get(key_name)]
    if missing_keys:
        instructions = "\n".join(
            f"  {key_name}: {KEY_SIGNUP_PAGES.get(key_name, 'see README.md at the top of the course folder')}"
            for key_name in missing_keys)
        raise RuntimeError(
            "This lab needs API keys that are not set yet. Add each one to\n"
            "the course's .env file as KEY_NAME=value, then re-run this cell:\n" + instructions)

# TAVILY_API_KEY powers the live web-search tool (free tier at tavily.com).
load_keys(["OPENAI_API_KEY", "TAVILY_API_KEY"])


# ======================================================================
# Notebook cell [8] — clients & imports (create_agent import moved to agent.py)
# ======================================================================
from openai import OpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

client = OpenAI()
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
chat_model = ChatOpenAI(model="gpt-6-luna")

print("All clients initialized ✅")
print(f"  Agent LLM: gpt-6-luna (via ChatOpenAI)")
print(f"  Embeddings: text-embedding-3-small")
print(f"  Web Search: Tavily API")


# ======================================================================
# Notebook cell [12] — resolve() helper
# ======================================================================
import os
def resolve(relative_path):
    """Find a pre-provided data file/folder across the likely locations."""
    for base_folder in ("", "../"):
        candidate_path = base_folder + relative_path
        if os.path.exists(candidate_path):
            return candidate_path
    raise FileNotFoundError(f"Could not find '{relative_path}'. On Colab, upload the data folder next to this notebook.")


# ======================================================================
# Notebook cell [14] — database path (path updated to data/database/)
# ======================================================================
DATABASE_PATH = resolve("data/database/meridian_wealth.db")

# Verify database exists and has data
assert os.path.exists(DATABASE_PATH), f"❌ Database not found at {DATABASE_PATH}. Ensure the data folder is present."


# ======================================================================
# Notebook cell [17] — load policy PDFs (path updated to data/docs)
# ======================================================================
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

POLICY_DIRECTORY = resolve("data/docs")
assert os.path.exists(POLICY_DIRECTORY), f"❌ Policy documents not found at {POLICY_DIRECTORY}/. Ensure the data folder is present."

# Step 1: Load all PDFs using LangChain's PyPDFLoader
all_pages = []
pdf_files = sorted([file_name for file_name in os.listdir(POLICY_DIRECTORY) if file_name.endswith(".pdf")])

print(f"📄 Loading {len(pdf_files)} policy PDFs...\n")
for pdf_file in pdf_files:
    loader = PyPDFLoader(os.path.join(POLICY_DIRECTORY, pdf_file))
    pages = loader.load()
    all_pages.extend(pages)
    print(f"   {pdf_file}: {len(pages)} pages loaded")

print(f"\n✅ Total pages extracted: {len(all_pages)}")


# ======================================================================
# Notebook cell [19] — split into chunks
# ======================================================================
# Step 2: Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,         # ~250 words per chunk — good for policy docs
    chunk_overlap=200,       # 200 char overlap prevents losing context at chunk boundaries
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]  # split on paragraphs first, then sentences
)

chunks = text_splitter.split_documents(all_pages)
print(f"✅ Split into {len(chunks)} chunks (chunk_size=1000, overlap=200)")


# ======================================================================
# Notebook cell [21] — embed + FAISS vector store
# ======================================================================
# Step 3 & 4: Embed and build FAISS vector store
print(f"\n⏳ Embedding {len(chunks)} chunks with text-embedding-3-small...")
policy_vectorstore = FAISS.from_documents(chunks, embedding_model)
policy_retriever_chain = policy_vectorstore.as_retriever(search_kwargs={"k": 4})

print(f"\n✅ FAISS vector store built:")
print(f"   Vectors: {policy_vectorstore.index.ntotal}")
print(f"   Embedding dimensions: 1,536")
print(f"   Retriever: top-4 similarity search")


# ======================================================================
# Notebook cell [25] — database query helpers
# ======================================================================
def query_database(sql_query, params=()):
    """Execute a SQL query against the Meridian Wealth database and return rows as dicts."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql_query, params)
    rows = [dict(table_row) for table_row in cursor.fetchall()]
    conn.close()
    return rows


def get_client_portfolio(client_id):
    """Get full portfolio for a client with enriched market data."""
    client = query_database("SELECT * FROM clients WHERE client_id = ?", (client_id,))
    if not client:
        return None
    holdings = query_database("""
        SELECT h.ticker, h.company_name, h.shares, h.avg_cost_basis, h.current_price,
               h.sector, h.purchase_date,
               m.ytd_return_pct, m.pe_ratio, m.analyst_rating, m.high_52w, m.low_52w
        FROM holdings h
        LEFT JOIN market_data m ON h.ticker = m.ticker
        WHERE h.client_id = ?
        ORDER BY (h.shares * h.current_price) DESC
    """, (client_id,))
    return {"client": client[0], "holdings": holdings}


def search_market_data(query):
    """Search market data by ticker, sector, or company name."""
    normalized_query = query.upper().strip()
    results = query_database("SELECT * FROM market_data WHERE ticker = ?", (normalized_query,))
    if not results:
        results = query_database(
            "SELECT * FROM market_data WHERE UPPER(sector) LIKE ? OR UPPER(company_name) LIKE ? OR ticker LIKE ?",
            (f"%{normalized_query}%", f"%{normalized_query}%", f"%{normalized_query}%")
        )
    return results


# ======================================================================
# Notebook cell [28] — agent tools
# ======================================================================
@tool
def portfolio_lookup(client_id: str) -> str:
    """Look up a client's portfolio from the database: holdings, allocation, total value, and risk profile.
    Use this when you need to know what a specific client owns or their investment profile.
    Input: client ID like 'CLT-001', 'CLT-002', etc."""

    portfolio = get_client_portfolio(client_id.upper())
    if not portfolio:
        available = [record["client_id"] for record in query_database("SELECT client_id FROM clients")]
        return f"Client {client_id} not found. Available: {', '.join(available)}"

    client_record = portfolio["client"]
    holdings = portfolio["holdings"]

    total_current = sum(holding["shares"] * holding["current_price"] for holding in holdings)
    total_cost = sum(holding["shares"] * holding["avg_cost_basis"] for holding in holdings)
    overall_return = ((total_current - total_cost) / total_cost) * 100

    sector_values = {}
    for holding in holdings:
        holding_value = holding["shares"] * holding["current_price"]
        sector_values[holding["sector"]] = sector_values.get(holding["sector"], 0) + holding_value
    sector_percentages = {sector: round((sector_value / total_current) * 100, 1)
                          for sector, sector_value in sector_values.items()}

    holdings_detail = []
    for holding in holdings:
        current_value = holding["shares"] * holding["current_price"]
        gain = ((holding["current_price"] - holding["avg_cost_basis"]) / holding["avg_cost_basis"]) * 100
        portfolio_weight = (current_value / total_current) * 100
        holdings_detail.append({
            "ticker": holding["ticker"], "company": holding["company_name"],
            "shares": holding["shares"], "avg_cost": holding["avg_cost_basis"],
            "current_price": holding["current_price"], "current_value": current_value,
            "unrealized_gain_pct": round(gain, 1), "portfolio_weight_pct": round(portfolio_weight, 1),
            "sector": holding["sector"], "ytd_return": holding["ytd_return_pct"],
            "analyst_rating": holding["analyst_rating"], "purchase_date": holding["purchase_date"]
        })

    result = {
        "client_id": client_record["client_id"], "name": client_record["name"],
        "relationship_manager": client_record["relationship_mgr"], "risk_profile": client_record["risk_profile"],
        "investment_horizon": client_record["investment_horizon"], "aum_inr": client_record["aum_inr"],
        "last_review": client_record["last_review"],
        "total_portfolio_value": round(total_current),
        "total_cost_basis": round(total_cost),
        "overall_return_pct": round(overall_return, 1),
        "sector_allocation": sector_percentages,
        "holdings": holdings_detail
    }
    return json.dumps(result, indent=2, ensure_ascii=False)


@tool
def market_data_search(query: str) -> str:
    """Search the market database for stock tickers or sectors. Returns current price, YTD returns,
    PE ratio, analyst ratings, 52-week range, and market cap. Use this when you need market
    performance data for specific stocks or want to compare sector performance.
    Input: a stock ticker (e.g. 'RELIANCE'), sector name (e.g. 'IT', 'Banking'), or company name."""

    results = search_market_data(query)
    if not results:
        all_tickers = [record["ticker"] for record in query_database("SELECT ticker FROM market_data")]
        return f"No data found for '{query}'. Available: {', '.join(all_tickers)}"

    formatted = [{
        "ticker": record["ticker"], "company": record["company_name"], "sector": record["sector"],
        "price": record["current_price"], "ytd_return": record["ytd_return_pct"],
        "pe_ratio": record["pe_ratio"], "analyst_rating": record["analyst_rating"],
        "52w_range": f"{record['low_52w']} - {record['high_52w']}",
        "market_cap_cr": record["market_cap_cr"]
    } for record in results]
    return json.dumps(formatted, indent=2, ensure_ascii=False)


@tool
def calculate_metrics(expression: str) -> str:
    """Perform financial calculations: returns, percentages, allocations, comparisons.
    Input: describe the calculation, e.g. 'return on 596000 vs cost 430000'
    or 'percentage of 350000 out of 2530000' or 'compare 18.5 vs 12.3'."""
    try:
        numbers = [float(token.replace(',', '')) for token in re.findall(r'[\d,]+\.?\d*', expression)]

        if "return" in expression.lower() or "gain" in expression.lower():
            if len(numbers) >= 2:
                current, cost = numbers[0], numbers[1]
                return_percent = ((current - cost) / cost) * 100
                return f"Return: (₹{current:,.0f} - ₹{cost:,.0f}) / ₹{cost:,.0f} = {return_percent:+.2f}%"

        if "percentage" in expression.lower() or "allocation" in expression.lower() or "weight" in expression.lower():
            if len(numbers) >= 2:
                part, whole = numbers[0], numbers[1]
                return f"Percentage: ₹{part:,.0f} / ₹{whole:,.0f} = {(part/whole)*100:.2f}%"

        if "compare" in expression.lower() and len(numbers) >= 2:
            first_value, second_value = numbers[0], numbers[1]
            return f"Comparison: {first_value:,.2f} vs {second_value:,.2f} | Diff: {first_value-second_value:+,.2f} ({((first_value-second_value)/second_value)*100:+.2f}%)"

        if len(numbers) == 2:
            first_value, second_value = numbers
            return f"Values: {first_value:,.2f} and {second_value:,.2f} | Sum: {first_value+second_value:,.2f} | Diff: {first_value-second_value:+,.2f} | Ratio: {first_value/second_value:.4f}"

        return f"Provide two numbers with operation type (return, percentage, compare). Got: '{expression}'"
    except Exception as error:
        return f"Calculation error: {str(error)}"


@tool
def policy_retriever(query: str) -> str:
    """Search Meridian Wealth Partners' investment policy PDF documents using RAG (vector similarity search).
    Use this when you need to check investment guidelines, allocation rules, rebalancing triggers,
    risk limits, concentration limits, suitability standards, or reporting requirements.
    Returns relevant excerpts with source document name and page number.
    Input: a natural language query about investment policies."""

    documents = policy_retriever_chain.invoke(query)
    results = []
    for rank, document in enumerate(documents, 1):
        source_name = os.path.basename(document.metadata.get("source", "unknown"))
        page_number = document.metadata.get("page", "?")
        results.append(f"[Policy Doc {rank}: {source_name} | Page {page_number}]\n{document.page_content}")
    return "\n\n---\n\n".join(results)


# ======================================================================
# Notebook cell [29] — Tavily web search + tools list
# ======================================================================
# Tavily web search — live market news
web_search = TavilySearch(max_results=3, topic="news")

# All tools
tools = [portfolio_lookup, market_data_search, calculate_metrics, policy_retriever, web_search]

print(f"✅ {len(tools)} tools defined:")
for agent_tool in tools:
    print(f"   🔧 {agent_tool.name}: {agent_tool.description[:80]}...")