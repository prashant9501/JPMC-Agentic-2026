# Agentic AI Mastery — Hands-On Labs

Design, build, evaluate, deploy and secure AI agents. This repository holds the hands-on labs, the data
files they read and the slide decks for the program. **All seven modules are here now**; updates are added to
this repository before their sessions.

## The program, module by module

| Module | What it covers |
|---|---|
| **1 · Foundations & First Agent** | Calling LLMs from four providers with validated, structured outputs; prompt engineering from zero-shot to Tree-of-Thought and Chain-of-Verification; prompt caching; making calls robust (retries, fallbacks, hallucination signals); and retrieval-augmented generation — loading and chunking documents, a complete RAG pipeline with citations, and advanced retrieval. **Available now — see the labs below.** |
| **2 · LangGraph Core Workflow Patterns** | Your first agents — tool calling and the ReAct loop, then **Project 1**, a financial-analyst agent that combines SQL, document RAG and web search. Then LangGraph's workflow patterns: routing, prompt chaining with quality gates, parallel fan-out / fan-in, and human-in-the-loop with memory and checkpointing. **Available now — see the labs below.** |
| **3 · Multi-Agent Architectures in LangGraph** | Supervisor, orchestrator-worker, evaluator-optimizer, swarm and reflection patterns — **Project 2**, a multi-agent customer-support system, and **Project 3**, a compliance report generator. **Available now — see the labs below.** |
| **4 · Multi-Framework Agent Development** | The OpenAI Agents SDK (handoffs, guardrails, tracing), a realtime voice agent and CrewAI (**Project 4**, a content pipeline) — and how to choose between frameworks. **Available now — see the labs below.** |
| **5 · Context Engineering & Agent Evaluations** | Context-window budgeting and compaction, reusable skills and prompt optimization, and three layers of evaluation: LLM, RAG and agent evals, with LLM-as-judge and pass@k. **Available now — see the labs below.** |
| **6 · Guardrails, Security, Observability & MCP/A2A** | A four-layer guardrail stack (prompt injection, PII redaction, output safety, human review), tracing with LangSmith and Langfuse, the Model Context Protocol and Agent-to-Agent protocol — **Project 5**, secure insurance-claims processing. **Available now — see the labs below.** |
| **7 · Production Deployment & Advanced Agents** | From notebook to service: FastAPI, Chainlit, Docker, nginx and AWS; managed models on AWS Bedrock; Google's Agent Development Kit (**Project 6**); multimodal agents. **Available now: the financial-analyst app — see below.** |

## Module 1 labs

| Lab | Title | What you do |
|---|---|---|
| 1.1 | Multi-Provider LLM Setup & Structured Outputs | Call OpenAI, Anthropic, Gemini and Groq; get validated Pydantic objects back from each; compare cost and latency; build a fallback chain. |
| 1.2 | Prompting Techniques & Structured Outputs | Messages and prompt templates, zero-shot and few-shot prompting, Chain-of-Thought, Tree-of-Thought, personas, and structured output inside a LangChain chain. |
| 1.3 | Chain-of-Verification (CoVe): Reducing Hallucinations | Have the model draft an answer, plan verification questions, check its own claims and write a corrected final answer. |
| 1.4 | Prompt Caching Across Providers (OpenAI · Anthropic · Gemini) | Structure prompts so long, stable prefixes are cached, and measure the token and cost savings on each provider. |
| 1.5 | LLM Robustness: Retries, Fallback & Hallucination Signals | Make LLM calls survive failure — retries with exponential backoff and jitter, a fallback provider, timeouts — and spot signs of hallucination; trace it all in LangSmith. |
| 1.6 | Document Loaders & Chunking | Load text, Markdown, CSV, JSON and PDF files with LangChain loaders, then split them with the main chunking strategies and see how chunk size changes what you get. |
| 1.7 | Complete RAG Pipeline with LCEL & Citations | Load, chunk, embed and index a banking-policy corpus in FAISS and Chroma; compare similarity and MMR retrieval; build an LCEL chain that answers with citations. |
| 1.8 | Advanced RAG Retrieval: Hybrid Search, HyDE, Re-Ranking & Contextual Chunks | Combine BM25 and vector search, generate hypothetical documents to search with, re-rank with a cross-encoder, and add context to chunks — then compare the strategies. |

### Slide decks

Each deck is a single HTML file: open it in any browser. In teaching order:

1. GenAI Fundamentals — A Beginner's Guide
2. Fundamentals of Prompt Engineering
3. RAG Systems Part 1: Embeddings & Vector Databases
4. RAG Systems Part 2: Architecture, Frameworks, Evaluation & Advanced Techniques

plus *AI Fundamentals & Applications in Banking* (`ai-fundamentals-banking-presentation.html`).

### Data files

Data files sit **beside the notebooks that read them**. Leave them where they are.

- `docs/` — nine banking-policy Markdown documents (Lab 1.7).
- `rag_docs/` — a Wikipedia extract and four research papers (Lab 1.8).
- `langchain_readme_sample.md`, `layoutparser_paper.pdf` and `Vision Transformers.pdf`, at the top of the
  module folder — the sample files Lab 1.6 loads.

## Module 2 labs

| Lab | Title | What you do |
|---|---|---|
| 2.1 | Agent Fundamentals: Tool Calling & the ReAct Loop | Use a built-in search tool and build your own with `@tool` and `StructuredTool`; bind tools to a model and read its `tool_calls`; build a ReAct agent with `create_agent` and debug it when it picks the wrong tool or a tool fails. |
| 2.2 | ⭐ **Project 1:** Financial Analyst Agentic RAG | A wealth-management agent with five tools — SQL lookups on a client-portfolio database, RAG over five policy PDFs, and live web search — that prepares client briefings, with its ReAct trace to debug. |
| 2.3 | LangGraph Routing | A customer-support router in LangGraph: classify each query with structured output and send it down a conditional edge to the right handler. |
| 2.4 | Prompt Chaining & Quality Gates | A healthcare-triage pipeline of chained nodes with quality gates and bounded retries, which hands genuinely ambiguous cases to a human. |
| 2.5 | Parallelization: Fan-Out / Fan-In with the Send API | Run independent compliance checks in parallel and merge their results; fan out dynamically with `Send`; measure what parallelism buys you. |
| 2.6 | Human-in-the-Loop, Memory & Checkpointing | A loan-approval graph that pauses with `interrupt()` for a human decision and resumes with `Command`; conversation memory with checkpointers and cross-session memory with `InMemoryStore`. |

### Slide deck

*Agentic AI: From Workflows to Autonomous Agents* (`1. agentic-ai-presentation.html`).

### Data files

- `docs/` — five investment-policy PDFs (Lab 2.2).
- `database/` — the wealth-management SQLite database (Lab 2.2).

## Module 3 labs

| Lab | Title | What you do |
|---|---|---|
| 3.1 | ⭐ **Project 2:** Customer Support Multi-Agent System | The ShopSmart support system, built with the Supervisor pattern: PII redaction, a supervisor that classifies and routes each ticket, a deterministic quick-answer path, four specialist agents with their own tools, policy RAG over FAISS, human escalation with `interrupt()` and thread memory — then routing accuracy measured across a batch of real tickets. |
| 3.2 | ⭐ **Project 3:** Compliance Report Generator | One orchestrator-worker graph writes regulatory reports for FinCEN, the OCC and a state banking department: sections planned from each regulator's template and drafted in parallel with `Send`, every figure grounded in the bank's data, an evaluator-optimizer loop that checks numbers, terminology and cross-references, a compliance officer's sign-off through human-in-the-loop, and checkpoint history as the audit trail. |
| 3.3 | Swarm Pattern: E-Commerce Order Lifecycle | Six agents pass an order between them peer to peer, with no supervisor, through handoff tools built on `Command`; test seven lifecycle scenarios (fraud, returns, stock-outs, payment failure); then rebuild it with the prebuilt `create_swarm` and decide when a swarm beats a supervisor. |
| 3.4 | Reflection: Content Quality Pipeline | A generate → critique → revise loop for fintech marketing copy: deterministic hard checks plus an LLM critic, best-so-far tracking and early stopping, and a multi-trial comparison of single-shot against reflective generation. |

### Data files

From this module on, each lab's data files sit in a **`Lab_3.N Files`** folder beside its notebook. Keep the
folder next to the notebook and keep its name.

- `Lab_3.1 Files/` — ShopSmart's customers, orders, products and support tickets (JSON) and its policies
  (Markdown).
- `Lab_3.2 Files/` — MidwestBank's customers, transactions, SAR filings and prior examination findings (CSV),
  its regulatory thresholds (JSON) and the three regulators' report templates (Markdown).
- Labs 3.3 and 3.4 build their data inside the notebook.

## Module 4 labs

| Lab | Title | What you do |
|---|---|---|
| 4.1 | OpenAI Agents SDK: Banking Concierge with Guardrails | A banking concierge built with the OpenAI Agents SDK: `@function_tool` tools, specialist agents connected by handoffs and as agents-as-tools, input and output guardrails, `SQLiteSession` memory and built-in tracing — then how the SDK compares with LangGraph. |
| 4.2 | Realtime Voice Agent: A Banking IVR You Can Talk To | Lab 4.1's concierge as a voice IVR: prompts written for the ear (pronunciation, preambles, confirmation before any action), a live speech-to-speech call with `RealtimeAgent`, semantic turn detection and barge-in, the Realtime API over a raw WebSocket, and an out-of-band compliance transcript. |
| 4.3 | ⭐ **Project 4:** CrewAI FinTech Content Pipeline | A crew of role-playing agents — researcher, writer, editor and compliance reviewer — with custom `@tool`s, run first as a sequential pipeline and then under a manager agent; then LangGraph, the OpenAI Agents SDK and CrewAI side by side, with a rule for choosing between them. |

The Module 4 labs need no data files.

## Module 5 labs

| Lab | Title | What you do |
|---|---|---|
| 5.1 | Context Window Management & Compaction | Run the ShopSmart support agent through a 30-turn conversation and watch its context window and its bill grow; then apply three fixes — history compaction, tool-result clearing and just-in-time retrieval — and measure what each one saves and what it costs. |
| 5.2 | Reusable Skills & Prompt Optimization | Package instructions as reusable skills an agent loads only when it needs them (progressive disclosure, `SKILL.md` files), score them with an LLM judge from a different model family, and improve the weakest skill with an evaluation-driven optimization loop. |
| 5.3 | Agent Eval Suite | Evaluate Project 2's multi-agent system on a 24-case labelled dataset with three grader types — rule-based routing checks, an LLM judge and tool-trajectory checks — then pass@k, judge calibration and a pytest gate for CI. |
| 5.4 | RAG Evaluation: Own Your Metrics | Evaluate Project 1's retrieval and answers over its 174-page policy corpus with metrics you implement yourself — recall@k, precision@k, MRR, nDCG, faithfulness and answer relevancy — choose `k` with evidence, and check the LLM judge against human labels. |

### Data files

As in Module 3, each lab's data files sit in a **`Lab_5.N Files`** folder beside its notebook. Keep the
folder next to the notebook and keep its name.

- `Lab_5.1 Files/` — ShopSmart's customers, orders, products and support tickets (JSON) and its policies
  (Markdown).
- `Lab_5.3 Files/` — the same ShopSmart data, plus `shopsmart_agent.py`: Project 2's system as a Python module,
  which the lab imports and evaluates. Open it — it is ordinary Python.
- `Lab_5.4 Files/docs/` — Project 1's five investment-policy PDFs.
- Lab 5.2 needs no data files.

## Module 6 labs

| Lab | Title | What you do |
|---|---|---|
| 6.1 | Four-Layer Guardrails: A Stack That Admits What It Misses | Wrap the ShopSmart support agent in four guardrail layers — prompt-injection screening, input sanitization, PII redaction with Presidio, and output safety — then run an adversarial suite that is written to find what the layers miss, and report it. |
| 6.2 | Observability with LangSmith & Langfuse | Trace the same ShopSmart routing agent in LangSmith and in Langfuse — tool calls, latency, cost, sessions and custom scores — and use the traces to answer the questions a production team gets asked, without archiving the customer's personal data. |
| 6.3 | MCP & A2A Protocol Deep Dive | Build a banking MCP server with FastMCP (tools, resources and prompts), call it over stdio and as a shared HTTP service, give an agent its read-only tools, then publish and discover A2A agent cards. |
| 6.4 | ⭐ **Project 5:** Secure Insurance Claims with MCP & A2A | A claims MCP server over the SecureLife database, A2A agent cards that split read and write privileges, and a guarded five-node LangGraph pipeline — triage, document check, fraud analysis, decision and compliance audit — traced in Langfuse and put through an adversarial test. |

### Slide decks

- *Observability, Evaluation & Responsible AI* (`Observability_Evaluation_Responsible_AI.html`) — the
  companion deck for Labs 5.2, 5.3, 6.1 and 6.2.
- *MCP — Part 1* and *MCP — Parts 2 & 3* (`MCP - Part 1.html`, `MCP - Part 2&3.html`) — for Labs 6.3 and 6.4.

### Data files

As in Modules 3 and 5, each lab's data files sit in a **`Lab_6.N Files`** folder beside its notebook.

- `Lab_6.1 Files/` and `Lab_6.2 Files/` — the ShopSmart customers, orders, products, support tickets and
  policies (each lab has its own copy).
- `Lab_6.4 Files/` — `SecureLife_claims.db`, the insurance-claims SQLite database.
- Lab 6.3 needs no data files.

## Module 7: the financial-analyst app

Module 7 takes an agent out of the notebook and turns it into an application. The first piece is
**`meridian-financial-app/`**: the Project 1 agent from Lab 2.2 — client portfolios from the SQL database, the
five investment-policy PDFs through RAG, and live web search — split into a small Python project with a
**Chainlit** chat interface in front of it.

| File | What it holds |
|---|---|
| `tools.py` | Key loading, the data paths, the FAISS index over the policy PDFs, the database helpers and the five tools — Lab 2.2's cells, in order |
| `agent.py` | The system prompt and the ReAct agent built with `create_agent` |
| `app.py` | The Chainlit interface: it sends each chat message to the agent and shows the answer |
| `requirements.txt` | The package versions the agent was built with, plus Chainlit |
| `data/` | `docs/` (the five policy PDFs) and `database/meridian_wealth.db` — the same files as Lab 2.2 |

**Run it.** Copy the module folder into `My Working Labs` like the others. With `My Working Labs` open in VS Code,
open a terminal (**Terminal → New Terminal**; it uses the `.venv` environment you selected) and run:

```bash
cd "Module 7 - Production Deployment & Advanced Agents\meridian-financial-app"
chainlit run app.py -w
```

Chainlit serves the chat at **http://localhost:8000** and opens it in your browser; `-w` reloads the app when you
save a file. The app reads `OPENAI_API_KEY` and `TAVILY_API_KEY` from your `.env` in `My Working Labs`. Each start
embeds the policy PDFs again, so the app takes a minute to come up. If the terminal says `chainlit` is not found,
install just that package with `pip install chainlit==2.12.0` — the agent's other packages are the ones Lab 2.2
already uses.

## Getting the labs onto your VM

Your training VM is already set up: a course folder on the Desktop holds the Python environment (`.venv`).
You will keep **two** folders next to it:

```
Desktop\<course folder>\
├── .venv\                  the Python environment (already there)
├── JPMC-Agentic-2026\      the cloned repository — git updates it; you never work in it
└── My Working Labs\        your copy — you run and edit the labs here
    └── .env                your API keys
```

### 1. Clone the repository (once)

Open a terminal in the course folder (in VS Code: **Terminal → New Terminal**) and run:

```bash
git clone https://github.com/prashant9501/JPMC-Agentic-2026.git
```

This creates the `JPMC-Agentic-2026` folder.

### 2. Make your working copy

Create a folder named **`My Working Labs`** in the course folder, next to `JPMC-Agentic-2026`. Copy each
module folder (for example `Module 1 - Foundations & First Agent`) from `JPMC-Agentic-2026` into
`My Working Labs` — with File Explorer, or from the terminal:

```bash
Copy-Item -Recurse "JPMC-Agentic-2026\Module 1 - Foundations & First Agent" "My Working Labs\"
```

**Run every lab from `My Working Labs`**, never from `JPMC-Agentic-2026`.

### 3. Add your keys

Your instructor gives you the API keys. Create a file named `.env` directly inside `My Working Labs`, one
key per line:

```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
GROQ_API_KEY=...
LANGSMITH_API_KEY=...
TAVILY_API_KEY=...
WEATHER_API_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
```

Every lab finds this file from its module folder. Because it sits outside `JPMC-Agentic-2026`, git never
uploads it and never overwrites it. Never paste a key into a notebook cell.

| Key | Used by |
|---|---|
| `OPENAI_API_KEY` | every lab, and the Module 7 app |
| `ANTHROPIC_API_KEY` | Labs 1.1, 1.4 and 1.8, Labs 5.1–5.4 (their judge models) and Lab 6.2 |
| `GEMINI_API_KEY` | Labs 1.1 and 1.4 |
| `GROQ_API_KEY` | Labs 1.1, 1.5 and 2.1 |
| `LANGSMITH_API_KEY` | Labs 1.5 and 6.2 (optional tracing in Lab 3.2) |
| `TAVILY_API_KEY` | Labs 2.1 and 2.2, and the Module 7 app |
| `WEATHER_API_KEY` | Lab 2.1 |
| `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` | Labs 6.2 and 6.4. They point at Langfuse's EU cloud; for a project in another region, add `LANGFUSE_HOST` (for example `https://us.cloud.langfuse.com`). |

Lab 6.2 checks for all five of its keys (OpenAI, Anthropic, LangSmith and both Langfuse keys) before it
starts. The Module 7 app needs only `OPENAI_API_KEY` and `TAVILY_API_KEY`.

### 4. Get new modules and updates

When your instructor announces new labs or fixes, update your clone:

```bash
cd JPMC-Agentic-2026
git pull
```

Then copy **only what is new** into `My Working Labs` — a new module folder, or a file your instructor says
was fixed. If File Explorer asks whether to replace a file you have been working in, choose **Skip** (or
rename your copy first), or your version is replaced.

> ⚠️ **Why not just run the labs inside `JPMC-Agentic-2026`?** Running a notebook saves its outputs into the
> file, so your clone now has local changes. The next time an update touches one of those files, `git pull`
> stops with *"Your local changes … would be overwritten by merge"* — and the quick way past that message
> throws your work away. That is why your drafts live in `My Working Labs`. If you are happy to lose them on
> every update, go ahead and work in the clone — your call 😛

## Your learning journal

`Learning Journal.md`, at the top of the repository, is a template for a five-minute reflection after each
lab: what it covered, what you learned, what is still unclear, and where you could use it in your work. Copy
it into `My Working Labs` and write in that copy, so `git pull` never overwrites it. Two example entries show
what a good entry looks like.

## Running a lab

1. In VS Code, open **`My Working Labs`** (**File → Open Folder**).
2. Open a lab notebook and select the `.venv` Python environment when VS Code asks for a kernel.
3. Run the cells from the top. Every notebook opens with the same set-up: a package cell (the packages are
   already installed on the VM, so its install line stays commented out), then `load_keys(...)`, which stops
   with instructions if a key the lab needs is missing.

Open each notebook from its own module folder: the labs read their data with paths relative to the notebook.

**Good to know**

- Some labs write working files as they run: `data.csv` and `chat_data.json` in Lab 1.6, the
  `chroma_banking/` and `banking_faiss_index/` vector stores in Lab 1.7, and the `quickloan_checkpoints.sqlite`
  checkpoint database in Lab 2.6, the `skills/` folder of `SKILL.md` files in Lab 5.2, and in Lab 5.3 the
  `test_shopsmart_evals.py` gate with its `.github/workflows/` CI template, and in Lab 6.3 the
  `banking_mcp_server.py` server it writes, its `.log` files and the `a2a_card_site/` folder. They are
  recreated on every run, so deleting them is always safe.
- Lab 6.4 writes to its database as it runs (status changes and audit rows in `SecureLife_claims.db`). To
  start from a clean database, copy `Lab_6.4 Files/SecureLife_claims.db` again from `JPMC-Agentic-2026`.
- Lab 6.3 starts its MCP server as a background process on port 8765 and stops it in Section 12. If you leave
  the lab before then, run Section 12 anyway, or the server keeps the port busy.
- The LangGraph labs (2.2–2.6, 3.1–3.4 and 6.4) draw each graph with `draw_mermaid_png()`, which calls the mermaid.ink web
  service — the VM needs internet access for those cells.
- Lab 1.8 downloads a small re-ranking model from Hugging Face the first time it runs.
- Lab 6.1's PII layer uses Presidio with spaCy's small English model, `en_core_web_sm`. If the lab reports
  the model missing, run the install lines in its Section 6 (they are commented out).
- **Lab 4.2's live voice call (its Section 5) needs a microphone and headphones** on the machine that runs the
  notebook. On the training VM it works only if your remote-desktop connection passes your microphone and
  audio through; if it does not, follow your instructor's demonstration for that section. Every other section
  of the lab is text-only and runs anywhere.
- Lab 1.6's optional high-resolution PDF cell needs Tesseract OCR and Poppler installed on the machine; every
  other cell runs without them.
- **One expected warning.** Labs 1.6, 1.7, 1.8, 2.2, 3.1, 5.3 and 5.4 import from `langchain-community`, which LangChain stopped
  maintaining in May 2026. The loaders and vector stores used from it have no maintained replacement yet, so
  the first import prints a `DeprecationWarning`, and the code works as shown.
