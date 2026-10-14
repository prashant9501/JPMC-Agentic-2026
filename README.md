# Agentic AI Mastery — Hands-On Labs

Design, build, evaluate, deploy and secure AI agents. This repository holds the hands-on labs, the data
files they read and the slide decks for the program. **Modules 1, 2 and 3 are here now**; each later module
is added to this repository before its sessions.

## The program, module by module

| Module | What it covers |
|---|---|
| **1 · Foundations & First Agent** | Calling LLMs from four providers with validated, structured outputs; prompt engineering from zero-shot to Tree-of-Thought and Chain-of-Verification; prompt caching; making calls robust (retries, fallbacks, hallucination signals); and retrieval-augmented generation — loading and chunking documents, a complete RAG pipeline with citations, and advanced retrieval. **Available now — see the labs below.** |
| **2 · LangGraph Core Workflow Patterns** | Your first agents — tool calling and the ReAct loop, then **Project 1**, a financial-analyst agent that combines SQL, document RAG and web search. Then LangGraph's workflow patterns: routing, prompt chaining with quality gates, parallel fan-out / fan-in, and human-in-the-loop with memory and checkpointing. **Available now — see the labs below.** |
| **3 · Multi-Agent Architectures in LangGraph** | Supervisor, orchestrator-worker, evaluator-optimizer, swarm and reflection patterns — **Project 2**, a multi-agent customer-support system, and **Project 3**, a compliance report generator. **Available now — see the labs below.** |
| **4 · Multi-Framework Agent Development** | The OpenAI Agents SDK (handoffs, guardrails, tracing), a realtime voice agent, CrewAI (**Project 4**, a content pipeline) and AutoGen — and how to choose between frameworks. |
| **5 · Context Engineering & Agent Evaluations** | Context-window budgeting and compaction, reusable skills and prompt optimization, and three layers of evaluation: LLM, RAG and agent evals, with LLM-as-judge and pass@k. |
| **6 · Guardrails, Security, Observability & MCP/A2A** | A four-layer guardrail stack (prompt injection, PII redaction, output safety, human review), tracing with LangSmith and Langfuse, the Model Context Protocol and Agent-to-Agent protocol — **Project 5**, secure insurance-claims processing. |
| **7 · Production Deployment & Advanced Agents** | From notebook to service: FastAPI, Chainlit, Docker, nginx and AWS; managed models on AWS Bedrock; Google's Agent Development Kit (**Project 6**); multimodal agents. |

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
```

Every lab finds this file from its module folder. Because it sits outside `JPMC-Agentic-2026`, git never
uploads it and never overwrites it. Never paste a key into a notebook cell.

| Key | Used by |
|---|---|
| `OPENAI_API_KEY` | every lab |
| `ANTHROPIC_API_KEY` | Labs 1.1, 1.4 and 1.8 |
| `GEMINI_API_KEY` | Labs 1.1 and 1.4 |
| `GROQ_API_KEY` | Labs 1.1, 1.5 and 2.1 |
| `LANGSMITH_API_KEY` | Lab 1.5 (optional tracing in Lab 3.2) |
| `TAVILY_API_KEY` | Labs 2.1 and 2.2 |
| `WEATHER_API_KEY` | Lab 2.1 |

Later modules need a few more keys; your instructor will give them to you with those modules.

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
  checkpoint database in Lab 2.6. They are recreated on every run, so deleting them is always safe.
- The LangGraph labs (2.2–2.6 and 3.1–3.4) draw each graph with `draw_mermaid_png()`, which calls the mermaid.ink web
  service — the VM needs internet access for those cells.
- Lab 1.8 downloads a small re-ranking model from Hugging Face the first time it runs.
- Lab 1.6's optional high-resolution PDF cell needs Tesseract OCR and Poppler installed on the machine; every
  other cell runs without them.
- **One expected warning.** Labs 1.6, 1.7, 1.8, 2.2 and 3.1 import from `langchain-community`, which LangChain stopped
  maintaining in May 2026. The loaders and vector stores used from it have no maintained replacement yet, so
  the first import prints a `DeprecationWarning`, and the code works as shown.
