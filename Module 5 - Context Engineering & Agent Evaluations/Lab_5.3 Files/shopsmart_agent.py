# -*- coding: utf-8 -*-
"""PROJECT 2 - the ShopSmart customer-support multi-agent system, as an importable module.

This is Lab 3.1's system, not a summary of it: the same PII redaction, the same FAISS policy
index, the same ten tools, the same four ReAct specialists with their exact tool allocations
and prompts, the same supervisor with its three escalation overrides, the same routing table.

WHY IT IS A SCRIPT AND NOT NOTEBOOK CELLS
-----------------------------------------
Lab 5.3 is about evaluation. Rebuilding the agent in cells before the first grader appears
buries the subject, and a notebook copy of an agent is a copy that drifts. Here it is imported,
so the lab evaluates the system you shipped rather than a lookalike of it.

Every function below is Lab 3.1's own code. Four are allowed to differ, for the four reasons
listed in Lab 5.3's section 2:

  1. The human manager is stubbed, not the HITL path. `interrupt()` fires for real and the
     payload is built; `process_ticket` resumes it immediately with SCRIPTED_MANAGER_NOTE,
     because an eval suite cannot wait for a human 24 times in a row.
  2. Progress prints are gated behind VERBOSE_AGENT. Lab 3.1 prints from every node, which is
     right for one ticket and unreadable across 24.

USAGE
-----
    from shopsmart_agent import process_ticket, TICKETS, TICKET_CATEGORIES

    final_state = process_ticket(TICKETS[0])
    print(final_state["category"], final_state["tools_used"])

Requires OPENAI_API_KEY in the environment. Run it directly for a one-ticket smoke test:

    python shopsmart_agent.py
"""

from datetime import datetime
from langchain.agents import create_agent
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph import START
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command
from pydantic import BaseModel, Field
from typing import Annotated, Literal, TypedDict, get_args
import json
import os
import re
import uuid

# ---- Models -----------------------------------------------------------------------------------
# Overridable from the environment so an eval run can swap the model without editing the agent -
# which is the whole point of having the agent in a file.
SUPERVISOR_MODEL_NAME = os.getenv("SHOPSMART_SUPERVISOR_MODEL", "gpt-5-mini")
SPECIALIST_MODEL_NAME = os.getenv("SHOPSMART_SPECIALIST_MODEL", "openai:gpt-5-mini")
FORMATTER_MODEL_NAME = os.getenv("SHOPSMART_FORMATTER_MODEL", "gpt-4.1-mini")

# A reasoning model: it does not accept `temperature`.
reasoning_model = ChatOpenAI(model=SUPERVISOR_MODEL_NAME)

# PROJECT 2's second model. `format_response_node` uses it to rewrite every specialist answer
# as an email, so THIS is the model whose output every grader actually scores.
llm_secondary = ChatOpenAI(model=FORMATTER_MODEL_NAME, temperature=0.3)


# ---- Data: PROJECT 2's five files ----------------------------------------------------------
# --- Spine A data: PROJECT 2's own files, loaded the way Lab 3.1 loads them ---
# These are the SAME five files Lab 3.1 (PROJECT 2) reads, byte for byte. Nothing is retyped
# and nothing is trimmed, so the join keys survive: a ticket carries a customer_id, a customer
# owns orders, an order references products. Every later lab in this spine depends on that.

def resolve_data_file(file_name):
    """Find one pre-provided Spine A data file across the likely locations.

    Colab users upload the "Lab_5.3 Files" folder next to the notebook; local users may run
    from the module directory or one level above it. Try each in turn.

    Args:
        file_name: a file inside the data folder, e.g. "orders.json".

    Returns:
        The first path that exists.

    Raises:
        FileNotFoundError: if none of the candidate locations contain it.
    """
    candidate_folders = (
        "Lab_5.3 Files/",
        "",
        "../Lab_5.3 Files/",
        "../",
    )
    for base_folder in candidate_folders:
        candidate_path = base_folder + file_name
        if os.path.exists(candidate_path):
            return candidate_path
    raise FileNotFoundError(
        f"Could not find '{file_name}'. On Colab, upload the 'Lab_5.3 Files' folder "
        f"next to this notebook."
    )


def load_json_data_file(file_name):
    """Load one pre-provided JSON data file and return its parsed contents."""
    with open(resolve_data_file(file_name), encoding="utf-8") as data_file:
        return json.load(data_file)


customers_raw = load_json_data_file("customers.json")
orders_raw = load_json_data_file("orders.json")
products_raw = load_json_data_file("products.json")
TICKETS = load_json_data_file("tickets.json")

with open(resolve_data_file("policies.md"), encoding="utf-8") as policies_file:
    POLICIES = policies_file.read()

# Index by primary key for O(1) lookup — exactly the three dictionaries Lab 3.1 builds.
CUSTOMERS_DB = {customer["customer_id"]: customer for customer in customers_raw}
ORDERS_DB = {order["order_id"]: order for order in orders_raw}
PRODUCTS_DB = {product["product_id"]: product for product in products_raw}

# Reverse index: which orders belong to which customer. This is the join a quick inline
# rewrite of this data tends to drop, and the reason a support agent can answer "what else have I ordered?".
CUSTOMER_ORDERS = {}
for order in orders_raw:
    CUSTOMER_ORDERS.setdefault(order["customer_id"], []).append(order)

# --- Split the real policy document into retrievable sections ---
# Just-in-time retrieval needs a corpus with parts. Rather than invent one, we split PROJECT 2's
# actual policies.md on its own top-level headings. The section names below are read OUT of the
# document, never hard-coded, so if the policy file changes this keeps working.

def split_policy_document(policy_markdown):
    """Split a markdown policy document into {section_name: section_text} on its "## " headings.

    Args:
        policy_markdown: the full contents of policies.md.

    Returns:
        An ordered dict-like mapping of lower-cased section key to the section's full text,
        heading included.
    """
    sections = {}
    current_key = None
    current_lines = []
    for line in policy_markdown.splitlines():
        if line.startswith("## "):
            if current_key is not None:
                sections[current_key] = "\\n".join(current_lines).strip()
            heading = line[3:].strip()
            current_key = heading.lower().replace(" & ", " ").replace(" ", "_")
            current_lines = [line]
        elif current_key is not None:
            current_lines.append(line)
    if current_key is not None:
        sections[current_key] = "\\n".join(current_lines).strip()
    return sections


POLICY_SECTIONS = split_policy_document(POLICIES)
ALL_POLICY_TEXT = "\\n\\n".join(POLICY_SECTIONS.values())


# ---- PII redaction ---------------------------------------------------------------------
# --- PROJECT 2's PII redaction, taken from Lab 3.1 without change ---
# The evaluation runs on the REDACTED text, exactly as PROJECT 2 does. That matters for an
# eval suite: if you grade the agent on raw text and ship it on redacted text, you measured a
# system you do not run. Every ticket in this corpus opens with a name and an email address,
# so this fires on all 100 of them.
#
# Module 6's guardrails lab replaces the regex-and-name-list approach below with Presidio NER and measures how
# much this one misses. It misses plenty - that is the guardrails lab's lesson, not this one's.


KNOWN_NAMES = {customer["name"] for customer in customers_raw}
KNOWN_FIRST_NAMES = {customer["name"].split()[0] for customer in customers_raw}
KNOWN_LAST_NAMES = {customer["name"].split()[-1] for customer in customers_raw}


def redact_pii(text: str, customer_id: str = None) -> tuple[str, dict]:
    """
    Redact PII from ticket text before sending to LLM.

    Args:
        text: The raw ticket text containing PII
        customer_id: Optional customer ID to look up specific name/email

    Returns:
        Tuple of (redacted_text, pii_mapping) where pii_mapping can be used
        to restore PII in the final response.
    """
    redacted = text
    pii_mapping = {}  # Maps placeholder -> original value

    # 1. Redact email addresses (regex)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails_found = re.findall(email_pattern, redacted)
    for email in emails_found:
        pii_mapping["[EMAIL_REDACTED]"] = email
        redacted = redacted.replace(email, "[EMAIL_REDACTED]")

    # 2. Redact phone numbers (multiple formats)
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    phones_found = re.findall(phone_pattern, redacted)
    for phone in phones_found:
        pii_mapping["[PHONE_REDACTED]"] = phone
        redacted = redacted.replace(phone, "[PHONE_REDACTED]")

    # 3. Redact known customer names (database-driven)
    for name in sorted(KNOWN_NAMES, key=len, reverse=True):  # longest first
        if name in redacted:
            pii_mapping["[NAME_REDACTED]"] = name
            redacted = redacted.replace(name, "[NAME_REDACTED]")

    if customer_id and customer_id in CUSTOMERS_DB:
        customer = CUSTOMERS_DB[customer_id]
        first_name = customer["name"].split()[0]
        if first_name in redacted and "[NAME_REDACTED]" not in pii_mapping:
            pii_mapping["[NAME_REDACTED]"] = customer["name"]
            redacted = redacted.replace(first_name, "[NAME_REDACTED]")

    return redacted, pii_mapping


def restore_pii(text: str, pii_mapping: dict) -> str:
    """Restore PII placeholders with original values for customer-facing response."""
    restored = text
    for placeholder, original in pii_mapping.items():
        restored = restored.replace(placeholder, original)
    return restored


# ---- Policy RAG index ------------------------------------------------------------------
# --- PROJECT 2's policy RAG index, taken from Lab 3.1 without change ---
# Same splitter, same separators, same chunk size, same embedding model, same k. The
# `policy_lookup` tool in the next cell retrieves from THIS index, so when the returns
# specialist quotes a return window it is quoting a retrieved chunk - not a policy string
# somebody pasted into a prompt.
#
# This is the part an evaluation lab is most tempted to skip, and the part that most changes
# the numbers. A retrieval miss and a reasoning failure produce the same wrong answer; only a
# suite that runs the real retriever can tell them apart.


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n## ", "\n### ", "\n- ", "\n", " "]
)

policy_chunks = text_splitter.split_text(POLICIES)

policy_documents = [
    Document(page_content=chunk, metadata={"source": "policies.md", "chunk_index": index})
    for index, chunk in enumerate(policy_chunks)
]

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
policy_vector_store = FAISS.from_documents(policy_documents, embeddings)

policy_retriever = policy_vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)


# ---- State, classification schema and the supervisor ---------------------------------
# --- The system under test: PROJECT 2's agent, taken from Lab 3.1 ---
# This is not a re-implementation of PROJECT 2's *pattern*. It is PROJECT 2's own code, with
# one thing removed and nothing renamed. Every class, function and graph-node name below is
# the name Lab 3.1 gave it, because an evaluation lab whose system under test you cannot
# recognise is measuring something you did not build.
#
# FOUR THINGS DIFFER, all forced, all listed in Lab 5.3's section 2. The one that surprises
# people:
#
#   The HUMAN is stubbed, not the HITL path. `interrupt()` fires exactly as Lab 3.1 wrote it
#   and the escalation payload is built; what an eval suite cannot do is WAIT, so
#   `process_ticket` resumes the graph immediately with a fixed SCRIPTED_MANAGER_NOTE. The
#   consequence is graded, not hidden: on that path the answer is the manager's text, so
#   Graders 2 and 3 exclude those cases instead of scoring them badly.
#
# Everything else is PROJECT 2's, running for real: the PII redaction, the FAISS policy index,
# the ten tools, the four ReAct specialists with their exact tool allocations and prompts, the
# supervisor's three business-rule overrides, the routing table, the checkpointer.
#
# That is the point. An evaluation of a reduced system tells you about the reduced system.


# Lab 3.1 prints a progress line from every node. That is right for one ticket and unreadable
# for twenty-four, so the prints are gated rather than deleted - flip this to watch one run.
VERBOSE_AGENT = False


class CustomerSupportState(TypedDict):
    """Shared state for the Customer Support Multi-Agent System.

    Lab 3.1's state, trimmed to the fields this evaluation reads. Field NAMES are unchanged:
    Module 6's guardrails lab swaps the regex redactor behind `redacted_text` for Presidio, and its
    observability lab writes
    audit records, both against these same keys.
    """
    messages: Annotated[list, add_messages]

    ticket_id: str
    customer_id: str
    customer_tier: str          # bronze / silver / platinum

    ticket_text: str            # original text, with PII --- NEVER sent to the LLM
    redacted_text: str          # PII-redacted version --- this goes to the LLM

    category: str               # order_status, returns, billing, product_inquiry, technical, escalation
    priority: str               # low, medium, high, critical
    classification_confidence: float

    specialist_response: str
    needs_escalation: bool
    human_notes: str            # notes a manager adds during HITL

    final_response: str

    tools_used: list[str]       # the recorded trajectory - Grader 3 reads this
    pii_mapping: dict           # placeholders -> original values, for the final response


class TicketClassification(BaseModel):
    """Structured output for ticket classification by the supervisor.

    Copied from Lab 3.1 without change. Note that it emits FIVE outputs, not one: the
    category, the priority, a confidence score, an escalation flag and the reasoning.
    Keeping only `category` would leave an evaluation unable to grade
    four of the five things PROJECT 2's supervisor actually decides.
    """
    category: Literal[
        "order_status",
        "returns",
        "billing",
        "product_inquiry",
        "technical",
        "escalation"
    ] = Field(description="The primary category of the support ticket")

    priority: Literal[
        "low",
        "medium",
        "high",
        "critical"
    ] = Field(description="Priority level based on urgency and customer tier")

    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0 for the classification",
        ge=0.0,
        le=1.0
    )

    requires_escalation: bool = Field(
        description=(
            "True if the ticket should be escalated to a human manager. "
            "Escalate when: (1) customer explicitly requests a manager, "
            "(2) ticket mentions legal action or social media threats, "
            "(3) category is 'escalation', or "
            "(4) issue involves a high-value dispute over $500."
        )
    )

    reasoning: str = Field(
        description="Brief explanation of why this category and priority were chosen"
    )


# The taxonomy is not one this lab invented: it is what `tickets.json` is LABELLED with, and
# `TicketClassification` above lists the same six. Deriving the evaluation's copy from the data
# rather than retyping it means the two cannot drift apart quietly - and the assert turns a
# drift into a failed cell instead of a mysteriously low routing score.
TICKET_CATEGORIES = sorted({ticket["category"] for ticket in TICKETS})
SCHEMA_CATEGORIES = sorted(get_args(TicketClassification.model_fields["category"].annotation))
assert TICKET_CATEGORIES == SCHEMA_CATEGORIES, (
    f"the data's labels {TICKET_CATEGORIES} and PROJECT 2's schema {SCHEMA_CATEGORIES} "
    f"disagree - routing accuracy would be measured against a taxonomy the agent cannot emit")

classifier_llm = reasoning_model.with_structured_output(TicketClassification)

SUPERVISOR_SYSTEM_PROMPT = """You are the ticket classification supervisor for ShopSmart customer support.

Your job is to classify incoming support tickets into the correct category and priority.

Categories:
- order_status: Questions about where an order is, tracking info, delivery estimates
- returns: Return requests, exchange requests, damaged/defective items
- billing: Payment issues, charges, invoices, refund status
- product_inquiry: Product questions, availability, specifications, recommendations
- technical: Account access issues, website problems, password resets
- escalation: Customer explicitly requests a manager, mentions legal action, or expresses extreme dissatisfaction

Priority guidelines:
- low: Simple questions, informational requests
- medium: Standard issues requiring action
- high: Urgent issues, frustrated customers, time-sensitive problems
- critical: Legal threats, safety issues, high-value disputes ($500+)

Escalation triggers (set requires_escalation=True):
- Customer explicitly asks for a manager or supervisor
- Mentions legal action, lawyer, or regulatory complaint
- Mentions social media threats ("I'll post this everywhere")
- Category is clearly 'escalation'
- High-value dispute over $500

Be precise and confident in your classification."""


# Lab 3.1's node, verbatim. The overrides below are the part worth noticing: two of the three
# fire on fields the classifier itself produced, so a badly calibrated `confidence` changes who
# gets a human. Section 7c measures whether that confidence is worth trusting.
def supervisor_router(state: CustomerSupportState) -> dict:
    """
    Supervisor node: classifies the ticket and determines routing.

    This node:
    1. Takes the redacted ticket text
    2. Uses LLM with structured output to classify
    3. Applies business rules for escalation overrides
    4. Returns the classification results to state
    """
    redacted_text = state["redacted_text"]
    customer_tier = state.get("customer_tier", "bronze")

    classification = classifier_llm.invoke([
        SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
        HumanMessage(content=f"Classify this support ticket:\n\n{redacted_text}")
    ])

    needs_escalation = classification.requires_escalation

    # Override: Platinum customers with high/critical priority ALWAYS escalate
    if customer_tier == "platinum" and classification.priority in ["high", "critical"]:
        needs_escalation = True

    # Override: Low confidence classifications escalate for human review
    if classification.confidence < 0.6:
        needs_escalation = True

    # Override: Explicit escalation category always escalates
    if classification.category == "escalation":
        needs_escalation = True

    if VERBOSE_AGENT:
        print(f"  [Supervisor] Category: {classification.category} | "
              f"Priority: {classification.priority} | "
              f"Confidence: {classification.confidence:.2f} | Escalation: {needs_escalation}")

    return {
        "category": classification.category,
        "priority": classification.priority,
        "classification_confidence": classification.confidence,
        "needs_escalation": needs_escalation,
        "tools_used": ["supervisor_classifier"],
        "messages": [
            AIMessage(content=f"Ticket classified as {classification.category} "
                              f"(priority: {classification.priority})")
        ]
    }


# ---- Tools and specialists -------------------------------------------------------------
# --- PROJECT 2's ten tools and four specialists, taken from Lab 3.1 ---
# These matter more here than they did in Lab 3.1. A tool call is an OBSERVABLE ACTION: it is
# recorded, it has a name, and it either happened or it did not. That is what makes Grader 3
# a real trajectory evaluator in this version rather than a substring search over prose.


@tool
def lookup_customer(customer_id: str) -> str:
    """Look up customer information by customer ID.
    Returns customer tier, join date, and ticket history.
    """
    if customer_id not in CUSTOMERS_DB:
        return f"Error: Customer {customer_id} not found in database."
    customer = CUSTOMERS_DB[customer_id]
    return json.dumps({
        "customer_id": customer["customer_id"],
        "name": "[REDACTED]",  # Never expose name through tool
        "tier": customer["tier"],
        "join_date": customer["join_date"],
        "past_tickets_count": customer["past_tickets_count"],
        "last_contact_date": customer["last_contact_date"]
    }, indent=2)


@tool
def lookup_order(order_id: str) -> str:
    """Look up a specific order by order ID.
    Returns order status, items, total, tracking number, and estimated delivery.
    """
    if order_id not in ORDERS_DB:
        return f"Error: Order {order_id} not found in database."
    order = ORDERS_DB[order_id]
    return json.dumps({
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "order_date": order["order_date"],
        "items": [{"name": item["name"], "quantity": item["quantity"], "price": item["price"]}
                  for item in order["items"]],
        "total": order["total"],
        "status": order["status"],
        "tracking_number": order["tracking_number"],
        "estimated_delivery": order["estimated_delivery"]
    }, indent=2)


@tool
def search_orders_by_customer(customer_id: str) -> str:
    """Find all orders for a given customer.
    Returns a summary list of all their orders with status.
    """
    if customer_id not in CUSTOMER_ORDERS:
        return f"No orders found for customer {customer_id}."
    orders = CUSTOMER_ORDERS[customer_id]
    summary = []
    for order in orders:
        summary.append({
            "order_id": order["order_id"],
            "order_date": order["order_date"][:10],
            "total": order["total"],
            "status": order["status"],
            "items_count": len(order["items"])
        })
    return json.dumps({"customer_id": customer_id, "order_count": len(summary),
                       "orders": summary}, indent=2)


@tool
def check_return_eligibility(order_id: str) -> str:
    """Check if an order is eligible for return based on ShopSmart's return policy.
    Standard items: 30 days from delivery. Electronics: 15 days.
    """
    if order_id not in ORDERS_DB:
        return f"Error: Order {order_id} not found."

    order = ORDERS_DB[order_id]

    if order["status"] != "delivered":
        return json.dumps({
            "order_id": order_id,
            "eligible": False,
            "reason": f"Order status is '{order['status']}'. Must be 'delivered' to process a return."
        })

    delivery_date = datetime.fromisoformat(order["estimated_delivery"])
    current_time = datetime.now()
    days_since_delivery = (current_time - delivery_date).days

    has_electronics = False
    for item in order["items"]:
        product_id = item.get("product_id", "")
        if product_id in PRODUCTS_DB and PRODUCTS_DB[product_id]["category"] == "Electronics":
            has_electronics = True
            break

    return_window = 15 if has_electronics else 30
    eligible = days_since_delivery <= return_window

    return json.dumps({
        "order_id": order_id,
        "eligible": eligible,
        "days_since_delivery": days_since_delivery,
        "return_window_days": return_window,
        "contains_electronics": has_electronics,
        "reason": "Within return window" if eligible
                  else f"Return window of {return_window} days has expired "
                       f"({days_since_delivery} days since delivery)"
    }, indent=2)


@tool
def lookup_product(product_id: str) -> str:
    """Look up detailed product information by product ID.
    Returns name, category, price, stock status, specs, and FAQ.
    """
    if product_id not in PRODUCTS_DB:
        return f"Error: Product {product_id} not found."
    product = PRODUCTS_DB[product_id]
    return json.dumps(product, indent=2)


@tool
def search_products(query: str) -> str:
    """Search products by name or category. Case-insensitive partial matching.
    Use this when the customer asks about a product by name.
    """
    query_lower = query.lower()
    results = []
    for product in PRODUCTS_DB.values():
        if query_lower in product["name"].lower() or query_lower in product["category"].lower():
            results.append({
                "product_id": product["product_id"],
                "name": product["name"],
                "category": product["category"],
                "price": product["price"],
                "stock_status": product["stock_status"]
            })
    if not results:
        return f"No products found matching '{query}'."
    return json.dumps({"query": query, "results_count": len(results),
                       "results": results}, indent=2)


@tool
def policy_lookup(query: str) -> str:
    """Search ShopSmart's official policies using semantic search.
    Use this to get accurate policy information about returns, shipping, billing, etc.
    """
    results = policy_retriever.invoke(query)
    if not results:
        return "No relevant policy information found."
    policy_text = "\n\n---\n\n".join([document.page_content for document in results])
    return f"Relevant ShopSmart Policies:\n\n{policy_text}"


@tool
def calculate_refund(order_id: str, reason: str) -> str:
    """Calculate the refund amount for an order based on the return reason.
    Defective items get full refund including shipping. Other returns exclude shipping.
    """
    if order_id not in ORDERS_DB:
        return f"Error: Order {order_id} not found."

    order = ORDERS_DB[order_id]
    total = order["total"]

    reason_lower = reason.lower()
    is_defective = any(word in reason_lower for word in
                       ["defective", "damaged", "broken", "wrong item", "incorrect"])

    if is_defective:
        refund_amount = total
        refund_type = "full (defective/damaged item)"
    else:
        shipping_cost = 0.0 if total > 50 else 5.99
        refund_amount = total - shipping_cost
        refund_type = "partial (shipping costs excluded)"

    return json.dumps({
        "order_id": order_id,
        "order_total": total,
        "refund_amount": round(refund_amount, 2),
        "refund_type": refund_type,
        "reason": reason,
        "processing_time": "5-7 business days"
    }, indent=2)


@tool
def check_billing_status(customer_id: str) -> str:
    """Check recent billing and payment information for a customer.
    Returns summary of recent orders and their payment status.
    """
    if customer_id not in CUSTOMER_ORDERS:
        return f"No billing records found for customer {customer_id}."

    orders = CUSTOMER_ORDERS[customer_id]
    recent_orders = sorted(orders, key=lambda order: order["order_date"], reverse=True)[:5]

    billing_records = []
    for order in recent_orders:
        billing_records.append({
            "order_id": order["order_id"],
            "order_date": order["order_date"][:10],
            "total": order["total"],
            "status": order["status"],
            "payment_status": "charged" if order["status"] != "cancelled" else "refunded"
        })

    return json.dumps({
        "customer_id": customer_id,
        "recent_billing": billing_records,
        "total_recent_charges": sum(record["total"] for record in billing_records
                                    if record["payment_status"] == "charged")
    }, indent=2)


@tool
def escalate_to_manager(reason: str) -> str:
    """Flag a ticket for escalation to a human support manager.
    Use when the issue is beyond automated handling capabilities.
    """
    escalation_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"
    return json.dumps({
        "escalation_id": escalation_id,
        "status": "escalated",
        "reason": reason,
        "message": "Ticket has been flagged for human manager review. "
                   "Expected response within 2 hours."
    }, indent=2)


# --- The four specialists, with Lab 3.1's exact tool allocations and prompts ---
order_specialist = create_agent(
    "openai:gpt-5-mini",
    tools=[lookup_order, search_orders_by_customer, lookup_customer],
    system_prompt=(
        "You are ShopSmart's order specialist. Help customers with order tracking, "
        "delivery status, and order issues.\n\n"
        "Guidelines:\n"
        "- Always look up the specific order when an order ID is mentioned\n"
        "- If no order ID is provided, search by customer ID\n"
        "- Provide specific tracking details and estimated delivery dates\n"
        "- Be empathetic if the order is delayed\n"
        "- For cancelled orders, explain next steps"
    ),
    name="order_specialist"
)

returns_specialist = create_agent(
    "openai:gpt-5-mini",
    tools=[lookup_order, check_return_eligibility, calculate_refund, policy_lookup],
    system_prompt=(
        "You are ShopSmart's returns specialist. Help with return requests, "
        "refund calculations, and exchange policies.\n\n"
        "Guidelines:\n"
        "- ALWAYS check return eligibility before promising a return\n"
        "- Look up the order to verify it exists and is delivered\n"
        "- Use policy_lookup for any policy questions\n"
        "- Calculate the refund amount before confirming\n"
        "- Clearly explain the return process and timeline"
    ),
    name="returns_specialist"
)

billing_specialist = create_agent(
    "openai:gpt-5-mini",
    tools=[check_billing_status, lookup_customer, lookup_order, policy_lookup],
    system_prompt=(
        "You are ShopSmart's billing specialist. Help customers with charges, "
        "invoices, refunds and payment questions.\n\n"
        "Guidelines:\n"
        "- Look up the customer's recent billing before answering\n"
        "- Quote the specific amount and order it relates to\n"
        "- Use policy_lookup for refund-timing questions\n"
        "- Never speculate about a charge you have not looked up"
    ),
    name="billing_specialist"
)

product_specialist = create_agent(
    "openai:gpt-5-mini",
    tools=[search_products, lookup_product, policy_lookup],
    system_prompt=(
        "You are ShopSmart's product specialist. Answer questions about products, "
        "availability, specifications and recommendations.\n\n"
        "Guidelines:\n"
        "- Search for the product the customer named before answering\n"
        "- Quote the price and stock status from the record\n"
        "- Use the product's specs and FAQ for detail questions\n"
        "- Never invent a specification"
    ),
    name="product_specialist"
)

SPECIALIST_TOOL_NAMES = {
    "order_specialist": ["lookup_order", "search_orders_by_customer", "lookup_customer"],
    "returns_specialist": ["lookup_order", "check_return_eligibility",
                           "calculate_refund", "policy_lookup"],
    "billing_specialist": ["check_billing_status", "lookup_customer",
                           "lookup_order", "policy_lookup"],
    "product_specialist": ["search_products", "lookup_product", "policy_lookup"],
}


# ---- Handler nodes, routing and the graph --------------------------------------------
# --- Handler nodes, routing and the graph: Lab 3.1's, node for node ---


# The stubbed human. Fixed on purpose: a manager whose reply varies between
# runs would make every escalated case irreproducible, and reproducibility is
# the only thing an eval harness really owes you.
SCRIPTED_MANAGER_NOTE = (
    "Reviewed and approved. I have acknowledged the customer's concern, applied a "
    "goodwill credit where policy allows, and asked the team to follow up within "
    "24 hours with a written resolution."
)


# =================================================================================================
# READ THIS BEFORE YOU READ ANY SCORE. There is a REAL BUG in PROJECT 2 below, kept on
# purpose, and it is the most interesting thing in this lab.
#
# Lab 3.1 picks the specialist's answer out of the returned messages with:
#
#     if hasattr(message, "content") and message.content and not hasattr(message, "tool_calls")
#
# `hasattr(message, "tool_calls")` is **always True for an AIMessage** - the field exists even
# when it is an empty list. So the condition never accepts the agent's actual answer. Walking
# the list in reverse, the first message that DOES satisfy it is the last `ToolMessage`, whose
# content is raw tool JSON.
#
# The consequence: `specialist_response` is usually a blob of JSON rather than prose. It is not
# obvious in Lab 3.1 because `format_response_node` then asks a second model to rewrite it as
# an email, and that model dutifully turns the JSON into readable text. The bug is real, it is
# shipped, and it degrades every specialist answer in the system.
#
# It ships FIXED. Lab 3.1's condition is preserved behind the switch below, so setting it to
# False reproduces Lab 3.1 exactly - which is what Lab 5.3's section 8 does, on purpose, to
# measure whether the eval suite can catch a one-line regression and say where it landed.
#
# The flag is read on EVERY call, so a notebook can flip it on the imported module object
# without re-importing or restarting its kernel.
USE_FIXED_RESPONSE_EXTRACTION = True


def _invoke_specialist(agent, agent_name, state):
    """Invoke a specialist agent, capture its answer, and record the tools it called.

    Lab 3.1's helper with three of section 2's four deviations: the tool calls are recorded
    (section 7c grades them), the prints are gated, and the response-extraction defect
    described above is FIXED unless USE_FIXED_RESPONSE_EXTRACTION is set to False.

    Args:
        agent: the compiled specialist agent.
        agent_name: its name, recorded in the trajectory.
        state: the current CustomerSupportState.

    Returns:
        A state update carrying the response and the recorded tool calls.
    """
    redacted_text = state["redacted_text"]
    customer_id = state.get("customer_id", "unknown")

    # Build context message for the specialist
    context = (
        f"Customer ID: {customer_id}\n"
        f"Ticket Category: {state.get('category', 'unknown')}\n"
        f"Priority: {state.get('priority', 'unknown')}\n"
        f"\nCustomer Message:\n{redacted_text}"
    )

    if VERBOSE_AGENT:
        print(f"  [{agent_name}] Processing ticket...")

    # Invoke the specialist agent
    result = agent.invoke(
        {"messages": [{"role": "user", "content": context}]}
    )

    # ADDED FOR THIS LAB: record the ACTUAL trajectory - every tool the agent called, in
    # order. Lab 3.1 records only the specialist's name, which cannot be graded.
    called_tool_names = []
    for message in result.get("messages", []):
        for tool_call in getattr(message, "tool_calls", None) or []:
            called_tool_names.append(tool_call["name"])

    # Extract the final response from the agent's messages
    response_text = ""
    if "messages" in result:
        for message in reversed(result["messages"]):
            if USE_FIXED_RESPONSE_EXTRACTION:
                # The fix: an answer is an AI message that made NO tool call.
                is_final_answer = (getattr(message, "content", "")
                                   and not (getattr(message, "tool_calls", None) or []))
            else:
                # Lab 3.1's condition, bug and all. See the note above.
                is_final_answer = (hasattr(message, "content") and message.content
                                   and not hasattr(message, "tool_calls"))
            if is_final_answer:
                response_text = message.content
                break

    if not response_text:
        response_text = "I apologize, but I was unable to process your request. Let me transfer you to a human agent."

    if VERBOSE_AGENT:
        print(f"  [{agent_name}] Response generated ({len(response_text)} chars)")
        print(f"  [{agent_name}] tools called: {called_tool_names}")

    return {
        "specialist_response": response_text,
        "tools_used": state.get("tools_used", []) + [agent_name] + called_tool_names,
        "messages": [AIMessage(content=f"[{agent_name}] {response_text[:200]}...")]
    }


def handle_order(state: CustomerSupportState) -> dict:
    """Handler node that invokes the order specialist agent."""
    return _invoke_specialist(order_specialist, "order_specialist", state)


def handle_returns(state: CustomerSupportState) -> dict:
    """Handler node that invokes the returns specialist agent."""
    return _invoke_specialist(returns_specialist, "returns_specialist", state)


def handle_billing(state: CustomerSupportState) -> dict:
    """Handler node that invokes the billing specialist agent."""
    return _invoke_specialist(billing_specialist, "billing_specialist", state)


def handle_product(state: CustomerSupportState) -> dict:
    """Handler node that invokes the product specialist agent."""
    return _invoke_specialist(product_specialist, "product_specialist", state)


# Lab 3.1's node, verbatim. It calls no LLM at all: if the ticket names an order, the answer
# is assembled from the record by a lookup table. Worth watching during evaluation - this path
# cannot hallucinate, and its grader scores should show it.
def quick_answer_node(state: CustomerSupportState) -> dict:
    """
    Deterministic quick-answer node for simple order status lookups.

    If the ticket mentions a specific order ID and the category is order_status,
    we look it up directly without calling an LLM.
    """
    redacted_text = state["redacted_text"]

    # Extract order ID from ticket text using regex
    order_match = re.search(r'ORD-\d{5}', redacted_text)

    if not order_match:
        # No specific order ID found --- cannot do quick answer
        return {
            "specialist_response": "I'd be happy to help with your order. Could you please provide your order number?",
            "tools_used": state.get("tools_used", []) + ["quick_answer_fallback"]
        }

    order_id = order_match.group()

    if order_id not in ORDERS_DB:
        return {
            "specialist_response": f"I could not find order {order_id} in our system. Please double-check the order number and try again.",
            "tools_used": state.get("tools_used", []) + ["quick_answer_lookup"]
        }

    order = ORDERS_DB[order_id]

    # Build deterministic response based on order status
    status = order["status"]
    tracking = order["tracking_number"]
    estimated_delivery = order["estimated_delivery"][:10]
    items_summary = ", ".join([item["name"] for item in order["items"]])

    status_messages = {
        "delivered": f"Your order {order_id} ({items_summary}) has been delivered. Tracking: {tracking}.",
        "in_transit": f"Your order {order_id} ({items_summary}) is currently in transit. Tracking: {tracking}. Estimated delivery: {estimated_delivery}.",
        "processing": f"Your order {order_id} ({items_summary}) is currently being processed. Tracking will be available once shipped. Estimated delivery: {estimated_delivery}.",
        "cancelled": f"Your order {order_id} ({items_summary}) was cancelled. If you did not request this cancellation, please let us know."
    }

    response = status_messages.get(status, f"Your order {order_id} has status: {status}.")

    if VERBOSE_AGENT:
        print(f"  [Quick Answer] Deterministic lookup for {order_id} -> status: {status}")

    return {
        "specialist_response": response,
        "tools_used": state.get("tools_used", []) + ["quick_answer_lookup"]
    }


def escalation_hitl_node(state: CustomerSupportState) -> dict:
    """
    Human-in-the-loop escalation node.

    Pauses the graph with interrupt() so a human manager can review the ticket.
    The human provides notes/instructions via Command(resume=...).
    """
    ticket_id = state.get("ticket_id", "unknown")
    customer_id = state.get("customer_id", "unknown")
    customer_tier = state.get("customer_tier", "unknown")
    category = state.get("category", "unknown")
    priority = state.get("priority", "unknown")
    redacted_text = state["redacted_text"]
    confidence = state.get("classification_confidence", 0.0)

    # Build escalation reason
    reasons = []
    if customer_tier == "platinum":
        reasons.append("Platinum customer (VIP)")
    if category == "escalation":
        reasons.append("Customer requested escalation")
    if confidence < 0.6:
        reasons.append(f"Low classification confidence ({confidence:.2f})")
    if priority in ["high", "critical"]:
        reasons.append(f"{priority.capitalize()} priority ticket")

    escalation_reason = "; ".join(reasons) if reasons else "Manual escalation"

    if VERBOSE_AGENT:
        print(f"  [HITL] Escalation triggered for ticket {ticket_id}")
        print(f"  [HITL] Reason: {escalation_reason}")
        print(f"  [HITL] Waiting for human manager input...")

    # Interrupt with rich payload for the human reviewer
    human_input = interrupt({
        "action": "escalation_review",
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "customer_tier": customer_tier,
        "category": category,
        "priority": priority,
        "classification_confidence": confidence,
        "redacted_text": redacted_text,
        "escalation_reason": escalation_reason,
        "instructions": (
            "Please review this ticket and provide:\n"
            "1. Your resolution notes\n"
            "2. Any special instructions for the customer response"
        )
    })

    # Human has responded via Command(resume=...)
    human_notes = human_input if isinstance(human_input, str) else str(human_input)

    if VERBOSE_AGENT:
        print(f"  [HITL] Human manager responded: {human_notes[:100]}...")

    return {
        "specialist_response": f"[Manager Review] {human_notes}",
        "human_notes": human_notes,
        "tools_used": state.get("tools_used", []) + ["escalation_hitl"],
        "messages": [AIMessage(content=f"Ticket escalated. Manager notes: {human_notes[:200]}")]
    }


# Lab 3.1's node, verbatim - and the one most worth reading before you trust a score.
#
# This node makes ANOTHER LLM CALL. The specialist's answer is not what reaches the customer;
# a second model rewrites it as an email first. So every grader downstream is scoring the
# REWRITE, not the specialist. If a tracking number survives the specialist and the formatter
# drops it, Grader 3 records a grounding failure - and it will be right to.
#
# The customer's first name comes from the DATABASE rather than from model output, which is
# why it cannot be hallucinated even though the model never saw the un-redacted text.
#
# NOTE A LATENT BUG, LEFT IN ON PURPOSE: `pii_mapping` is read from state and then never
# used - `restore_pii` is never called on this path. So if a specialist echoed a
# `[NAME_REDACTED]` placeholder, it reaches the customer verbatim. That is PROJECT 2's
# behaviour, not a porting slip, and fixing it here would mean evaluating a system
# nobody runs. Watch for it in the Grader 2 output - this is the sort of thing an
# evaluation is supposed to surface.
def format_response_node(state: CustomerSupportState) -> dict:
    """
    Format the specialist's response into a professional customer-facing message.
    Restores customer name from PII mapping for personalization.
    """
    specialist_response = state.get("specialist_response", "")
    pii_mapping = state.get("pii_mapping", {})
    customer_id = state.get("customer_id", "")
    ticket_id = state.get("ticket_id", "")

    # Get customer name for greeting (from database, not from LLM output)
    customer_name = "Valued Customer"
    if customer_id in CUSTOMERS_DB:
        customer_name = CUSTOMERS_DB[customer_id]["name"].split()[0]  # First name

    # Use LLM to format the response professionally
    format_prompt = f"""Rewrite the following customer support response as a professional,
friendly email response from ShopSmart Customer Support.

Customer's first name: {customer_name}
Ticket ID: {ticket_id}

Guidelines:
- Start with a personalized greeting using the customer's first name
- Be empathetic and professional
- Include all the specific details from the response (order numbers, tracking, dates)
- End with an offer for further assistance
- Sign off as "ShopSmart Customer Support Team"
- Keep it concise but complete

Original response to reformat:
{specialist_response}"""

    formatted = llm_secondary.invoke([
        HumanMessage(content=format_prompt)
    ])

    final_response = formatted.content

    if VERBOSE_AGENT:
        print(f"  [Formatter] Response formatted ({len(final_response)} chars)")

    return {
        "final_response": final_response,
        "tools_used": state.get("tools_used", []) + ["response_formatter"]
    }


# Lab 3.1's routing table, copied without change - INCLUDING the line that sends `technical`
# to the order specialist. That is a real gap in PROJECT 2, not a typo here, and section 7c is
# where this suite finds it on its own.
def route_ticket(state: CustomerSupportState) -> str:
    """
    Routing function used by conditional edges after the supervisor.

    Determines which handler node should process the ticket based on:
    1. Whether escalation is needed (overrides everything)
    2. Whether it is a simple order status query (quick_answer path)
    3. The classified category (routes to appropriate specialist)
    """
    # Check escalation first (highest priority)
    if state.get("needs_escalation", False):
        return "escalation"

    category = state.get("category", "")

    # For order_status with a specific order ID, use quick_answer (no LLM)
    if category == "order_status":
        redacted_text = state.get("redacted_text", "")
        has_order_id = bool(re.search(r'ORD-\d{5}', redacted_text))
        if has_order_id:
            return "quick_answer"
        return "order_handler"  # No specific order ID, needs agent to investigate

    # Route to appropriate specialist
    category_to_handler = {
        "returns": "returns_handler",
        "billing": "billing_handler",
        "product_inquiry": "product_handler",
        "technical": "order_handler",  # Technical issues handled by order specialist for now
        "escalation": "escalation",
    }

    return category_to_handler.get(category, "order_handler")


builder = StateGraph(CustomerSupportState)

builder.add_node("supervisor", supervisor_router)
builder.add_node("quick_answer", quick_answer_node)
builder.add_node("order_handler", handle_order)
builder.add_node("returns_handler", handle_returns)
builder.add_node("billing_handler", handle_billing)
builder.add_node("product_handler", handle_product)
builder.add_node("escalation", escalation_hitl_node)
builder.add_node("format_response", format_response_node)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges(
    "supervisor",
    route_ticket,
    {
        "quick_answer": "quick_answer",
        "order_handler": "order_handler",
        "returns_handler": "returns_handler",
        "billing_handler": "billing_handler",
        "product_handler": "product_handler",
        "escalation": "escalation",
    }
)

HANDLER_NODES = ["quick_answer", "order_handler", "returns_handler",
                 "billing_handler", "product_handler", "escalation"]
for handler_node in HANDLER_NODES:
    builder.add_edge(handler_node, "format_response")
builder.add_edge("format_response", END)

# Lab 3.1 compiles with a checkpointer and a store. The checkpointer is kept, because the
# HITL escalation path genuinely needs it: the graph interrupts, and `process_ticket`
# resumes it on the SAME thread a few lines further down.
#
# What it must NOT do is make two separate evaluation runs share state. See the note on
# `process_ticket` below: a fresh thread per call is the default, and resuming is opt-in.
memory = InMemorySaver()
compiled_agent = builder.compile(checkpointer=memory)


def process_ticket(ticket, thread_id=None, manager_note=SCRIPTED_MANAGER_NOTE):
    """Process a single ticket through the full multi-agent system.

    Lab 3.1's entry point, with its prints gated. Note what happens before the graph runs:
    the customer's tier is looked up and the text is redacted. Both feed decisions the
    supervisor makes, so an eval harness that skipped either would be running a different
    system from the one PROJECT 2 ships.

    Args:
        ticket: a ticket dict from tickets.json, or a TEST_DATASET case.
        thread_id: optional thread ID, ONLY for when you want to continue an existing
            conversation. Leave it unset for evaluation: each call then runs on its own
            fresh thread and is independent of every other call.
        manager_note: what the stubbed human manager says when the graph interrupts.

    Returns:
        The final CustomerSupportState after processing.
    """
    ticket_id = ticket.get("ticket_id") or ticket["id"]
    ticket_text = ticket.get("text") or ticket["query"]
    customer_id = ticket["customer_id"]

    # A FRESH thread per call, unless the caller names one.
    #
    # This used to default to a stable f"thread-{ticket_id}". Stable means RESUMING: the
    # second call for a ticket loaded the first call's checkpoint and inherited its
    # accumulated `messages`, so it graded a continuation rather than a new attempt. On a
    # cold kernel that is invisible; re-run any grader cell and it silently stops being a
    # clean measurement. Every metric in this lab assumes runs are independent, so the
    # dangerous behaviour must not be the one you get by saying nothing.
    #
    # Freshness is now the default and CONTINUITY IS OPT-IN - pass an explicit thread_id
    # when you actually want multi-turn state. The ticket id stays in the generated value
    # so a checkpoint is still traceable back to the case that produced it.
    if thread_id is None:
        thread_id = f"thread-{ticket_id}-{uuid.uuid4().hex[:8]}"

    customer = CUSTOMERS_DB.get(customer_id, {})
    customer_tier = customer.get("tier", "bronze")

    redacted_text, pii_mapping = redact_pii(ticket_text, customer_id)

    initial_state = {
        "messages": [HumanMessage(content=redacted_text)],
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "customer_tier": customer_tier,
        "ticket_text": ticket_text,
        "redacted_text": redacted_text,
        "category": "",
        "priority": "",
        "classification_confidence": 0.0,
        "specialist_response": "",
        "needs_escalation": False,
        "human_notes": "",
        "final_response": "",
        "tools_used": [],
        "pii_mapping": pii_mapping,
    }

    if VERBOSE_AGENT:
        print(f"PROCESSING TICKET: {ticket_id}  customer {customer_id} ({customer_tier})")
        print(f"Redacted: {redacted_text}")

    configuration = {"configurable": {"thread_id": thread_id}}
    final_state = compiled_agent.invoke(initial_state, configuration)

    # PROJECT 2 stops here and waits for a human manager. An evaluation suite cannot: it would
    # block on the first escalated ticket and never reach a metric. So the MANAGER is stubbed -
    # a fixed note, resumed immediately - while the HITL path itself runs for real. The
    # interrupt fires, the payload is built, `human_notes` is populated.
    #
    # Read the consequence before you read the scores: on this path the answer IS the manager's
    # text, so Graders 2 and 3 would be grading SCRIPTED_MANAGER_NOTE rather than the agent.
    # Section 5 and 6 exclude these cases for exactly that reason.
    if "__interrupt__" in final_state:
        final_state = compiled_agent.invoke(Command(resume=manager_note), configuration)
    return final_state

# ---- Introspection ----------------------------------------------------------------------------
def describe():
    """Return a one-line-per-fact summary of what this module built.

    The notebook prints this after importing, so the learner can see the system exists
    without the module printing anything on import.

    Returns:
        A list of human-readable strings.
    """
    return [
        f"data      : {len(CUSTOMERS_DB)} customers, {len(ORDERS_DB)} orders, "
        f"{len(PRODUCTS_DB)} products, {len(TICKETS)} tickets",
        f"policy    : {len(policy_chunks)} chunks indexed in FAISS, retrieving k=3",
        f"taxonomy  : {TICKET_CATEGORIES}",
        f"graph     : supervisor + {len(HANDLER_NODES)} handlers + format_response",
        f"tools     : {sorted(TOOL_REGISTRY)}",
        f"models    : supervisor={SUPERVISOR_MODEL_NAME}, "
        f"specialists={SPECIALIST_MODEL_NAME}, formatter={FORMATTER_MODEL_NAME}",
    ]


# Every tool the specialists can reach, by name. The evaluation's trajectory grader checks
# recorded calls against this, so a tool renamed here is caught rather than scored as a miss.
TOOL_REGISTRY = {
    "lookup_customer": lookup_customer,
    "lookup_order": lookup_order,
    "search_orders_by_customer": search_orders_by_customer,
    "check_return_eligibility": check_return_eligibility,
    "lookup_product": lookup_product,
    "search_products": search_products,
    "policy_lookup": policy_lookup,
    "calculate_refund": calculate_refund,
    "check_billing_status": check_billing_status,
    "escalate_to_manager": escalate_to_manager,
}


if __name__ == "__main__":
    VERBOSE_AGENT = True
    for fact in describe():
        print(fact)
    print()
    print("Smoke test on the first ticket:")
    smoke_state = process_ticket(TICKETS[0])
    print(f"  category  : {smoke_state['category']} (labelled {TICKETS[0]['category']})")
    print(f"  priority  : {smoke_state['priority']} (labelled {TICKETS[0]['priority']})")
    print(f"  confidence: {smoke_state['classification_confidence']:.2f}")
    print(f"  tools     : {smoke_state['tools_used']}")
    print(f"  response  : {smoke_state['final_response'][:160]}...")
