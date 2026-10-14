# My Learning Journal — Agentic AI Mastery

A five-minute habit: after each lab, write down what it covered, what you learned, what is still unclear,
and where you could use it in your own work. By the end of the program this is your personal reference,
and the "still unclear" lines are your questions for the next session.

## How to use it

1. **Copy this file into `My Working Labs`** and write in that copy, so `git pull` never overwrites it. In
   File Explorer, or from the course folder:

   ```bash
   Copy-Item "JPMC-Agentic-2026\Learning Journal.md" "My Working Labs\"
   ```

2. **Fill in one entry right after each lab**, while it is fresh. Short bullet points in your own words beat
   long paragraphs. In VS Code, **Ctrl+Shift+V** shows the formatted preview.
3. **Be honest under "Still unclear".** It is the most useful line in the entry: bring it to the next
   session or ask your instructor.
4. **Keep work examples general.** Describe the kind of task ("sorting incoming service requests"), never
   client data, account details, internal system names, credentials or anything confidential.

## What each entry asks

| Line | What to write | Sentence starters |
|---|---|---|
| **Covered** | The lab's topic in one or two sentences, in your own words | "This lab showed how to …" · "The core pattern was …" |
| **I learned** | Three takeaways: a concept, an API, a design choice | "I didn't know that …" · "The key piece is … because …" |
| **Clicked** | What you could now explain to a colleague | "I could explain why …" |
| **Still unclear** | What you could not yet explain or rebuild, as a question | "I followed the code but not why …" · "I got lost at …" · "My question is …" |
| **I tried** | One change you made in the notebook and what happened | "I changed … and saw …" |
| **At work: where** | A task or process in your team this could help with | "In my team, … could …" |
| **At work: first step** | The smallest experiment you could run in the next month | "A first prototype would …" |
| **At work: watch out for** | Data, approvals, risks and guardrails it would need | "Before this touches real data we'd need …" |

**Confidence (1–5):** 1 = I followed along · 3 = I could adapt it with the notebook open · 5 = I could
build it from scratch.

---

## Two example entries

### Example — Lab 2.3 · LangGraph Routing

*Confidence: 4*

- **Covered:** A LangGraph `StateGraph` that classifies a ShopSmart support query into a Pydantic
  `RouteDecision` and sends it down a conditional edge to the matching handler node.
- **I learned:**
  1. The router returns a validated object, not free text: the `Literal` list is the only set of categories
     it can answer with, so a misroute is a wrong category, never an invented one.
  2. The LLM classifies, but a plain Python routing function on the conditional edge decides where the
     query goes, so the routing logic stays readable and testable.
  3. `draw_mermaid_png()` draws the graph, which is the quickest way to check the wiring before running it.
- **Clicked:** How state builds up: each node returns only the fields it changes, and LangGraph merges them
  into the shared state.
- **Still unclear:** When I would choose the Functional API (`@entrypoint` / `@task`) over a `StateGraph`
  for a real workflow.
- **I tried:** Wrote three tickets that mix two requests. One went to a queue I would not have picked, so
  next I want to tighten the category descriptions and re-run them.
- **At work: where:** Our team's shared mailbox is sorted into four queues by hand every morning. A router
  like this could propose the queue and a priority for each request.
- **At work: first step:** Run it in "suggest only" mode on a week of anonymised subject lines and compare
  its choices with the queues people actually picked.
- **At work: watch out for:** The mailbox can contain customer details, so redaction comes first, and data
  governance signs off before any real message reaches an LLM. A person keeps the final say until we know
  how often it agrees with us.

### Example — Lab 3.1 · Project 2: Customer Support Multi-Agent System

*Confidence: 3*

- **Covered:** A supervisor classifies each support ticket and routes it to a no-LLM quick answer, one of
  four specialist agents with their own tools, or a human escalation, with personal data redacted before
  any model sees the text.
- **I learned:**
  1. The supervisor is a plain graph node with structured output, not an agent, so routing stays
     predictable. Only the specialists reason with tools.
  2. Not every path needs an LLM: an order-status ticket that quotes an order ID gets a deterministic
     answer, which is faster, cheaper and always the same.
  3. Escalation is a rule in code (a platinum customer with high or critical priority, an escalation
     category, or low classifier confidence), and `interrupt()` pauses the graph until a person responds.
- **Clicked:** Why redaction happens first, and why the original values come back only in the final reply
  to the customer.
- **Still unclear:** How the human's answer gets back into a paused graph (`Command(resume=...)`) when the
  system runs as a service rather than in a notebook. And would the redaction patterns catch the account
  and reference formats we use?
- **I tried:** Re-ran the routing-accuracy check on the first 20 tickets after rewording one category's
  description, and compared which tickets were misrouted before and after.
- **At work: where:** Internal operations requests: a supervisor that routes to "access request",
  "report problem" and "data correction" helpers, each with read-only lookups.
- **At work: first step:** Agree the categories and escalation rules with the team on paper, then build only
  the supervisor and measure its accuracy on past, anonymised requests before adding any specialist.
- **At work: watch out for:** Tool permissions. Specialists only read; anything that changes data goes
  through a person, with an audit trail of who approved what.

---

## My entries

### Module 1 · Foundations & First Agent

#### Lab 1.1 — Multi-Provider LLM Setup & Structured Outputs
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 1.2 — Prompting Techniques & Structured Outputs
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 1.3 — Chain-of-Verification (CoVe): Reducing Hallucinations
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 1.4 — Prompt Caching Across Providers
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 1.5 — LLM Robustness: Retries, Fallback & Hallucination Signals
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 1.6 — Document Loaders & Chunking
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 1.7 — Complete RAG Pipeline with LCEL & Citations
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 1.8 — Advanced RAG Retrieval: Hybrid Search, HyDE, Re-Ranking & Contextual Chunks
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Module 1 wrap-up
- **The technique I'd reach for first, and why:**
- **How the labs connect:**
- **One idea for my team that combines several of these labs:**
- **Still unclear across the module:**

### Module 2 · LangGraph Core Workflow Patterns

#### Lab 2.1 — Agent Fundamentals: Tool Calling & the ReAct Loop
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 2.2 — Project 1: Financial Analyst Agentic RAG
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 2.3 — LangGraph Routing
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 2.4 — Prompt Chaining & Quality Gates
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 2.5 — Parallelization: Fan-Out / Fan-In with the Send API
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 2.6 — Human-in-the-Loop, Memory & Checkpointing
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Module 2 wrap-up
- **The pattern I'd reach for first, and why:**
- **How the labs connect:**
- **One idea for my team that combines several of these labs:**
- **Still unclear across the module:**

### Module 3 · Multi-Agent Architectures in LangGraph

#### Lab 3.1 — Project 2: Customer Support Multi-Agent System
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 3.2 — Project 3: Compliance Report Generator
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 3.3 — Swarm Pattern: E-Commerce Order Lifecycle
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Lab 3.4 — Reflection: Content Quality Pipeline
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**

#### Module 3 wrap-up
- **The pattern I'd reach for first, and why:**
- **How the labs connect:**
- **One idea for my team that combines several of these labs:**
- **Still unclear across the module:**

---

## A blank entry for later modules

Copy this block for each new lab.

#### Lab __ — ____
*Date:* · *Confidence (1–5):*
- **Covered:**
- **I learned:**
  1.
  2.
  3.
- **Clicked:**
- **Still unclear:**
- **I tried:**
- **At work: where:**
- **At work: first step:**
- **At work: watch out for:**
