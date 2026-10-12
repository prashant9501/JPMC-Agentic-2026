# Agentic AI Mastery — Hands-On Labs

Design, build, evaluate, deploy and secure AI agents. This repository holds the hands-on labs, the data
files they read and the slide decks for the program. **Module 1 is here now**; each later module is added
to this repository before its sessions.

## The program, module by module

| Module | What it covers |
|---|---|
| **1 · Foundations & First Agent** | Calling LLMs from four providers with validated, structured outputs; prompt engineering from zero-shot to Tree-of-Thought; making calls robust (retries, fallbacks, hallucination signals); Chain-of-Verification; prompt caching; and retrieval-augmented generation — loading and chunking documents, a complete RAG pipeline with citations, and advanced retrieval. **Available now — see the labs below.** |
| **2 · LangGraph Core Workflow Patterns** | Your first agents — tool calling and the ReAct loop, then **Project 1**, a financial-analyst agent that combines SQL, document RAG and web search. Then LangGraph's workflow patterns: routing, prompt chaining with quality gates, parallel fan-out / fan-in, and human-in-the-loop with memory and checkpointing. |
| **3 · Multi-Agent Architectures in LangGraph** | Supervisor, orchestrator-worker, evaluator-optimizer, swarm and reflection patterns — **Project 2**, a multi-agent customer-support system, and **Project 3**, a compliance report generator. |
| **4 · Multi-Framework Agent Development** | The OpenAI Agents SDK (handoffs, guardrails, tracing), a realtime voice agent, CrewAI (**Project 4**, a content pipeline) and AutoGen — and how to choose between frameworks. |
| **5 · Context Engineering & Agent Evaluations** | Context-window budgeting and compaction, reusable skills and prompt optimization, and three layers of evaluation: LLM, RAG and agent evals, with LLM-as-judge and pass@k. |
| **6 · Guardrails, Security, Observability & MCP/A2A** | A four-layer guardrail stack (prompt injection, PII redaction, output safety, human review), tracing with LangSmith and Langfuse, the Model Context Protocol and Agent-to-Agent protocol — **Project 5**, secure insurance-claims processing. |
| **7 · Production Deployment & Advanced Agents** | From notebook to service: FastAPI, Chainlit, Docker, nginx and AWS; managed models on AWS Bedrock; Google's Agent Development Kit (**Project 6**); multimodal agents. |
| **8 · Capstone Project** | One end-to-end system that brings the course together: build, evaluate, secure and deploy. |

## Module 1 labs

| Lab | Title | What you do |
|---|---|---|
| 1.1 | Multi-Provider LLM Setup & Structured Outputs | Call OpenAI, Anthropic, Gemini and Groq; get validated Pydantic objects back from each; compare cost and latency; build a fallback chain. |
| 1.2 | Prompting Techniques & Structured Outputs | Messages and prompt templates, zero-shot and few-shot prompting, Chain-of-Thought, Tree-of-Thought, personas, and structured output inside a LangChain chain. |
| 1.3 | LLM Robustness: Retries, Fallback & Hallucination Signals | Make LLM calls survive failure — retries with exponential backoff and jitter, a fallback provider, timeouts — and spot signs of hallucination; trace it all in LangSmith. |
| 1.4 | Chain-of-Verification (CoVe): Reducing Hallucinations | Have the model draft an answer, plan verification questions, check its own claims and write a corrected final answer. |
| 1.5 | Prompt Caching Across Providers (OpenAI · Anthropic · Gemini) | Structure prompts so long, stable prefixes are cached, and measure the token and cost savings on each provider. |
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

Create a folder named **`My Working Labs`** in the course folder, next to `JPMC-Agentic-2026`. Copy the
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
```

Every lab finds this file from its module folder. Because it sits outside `JPMC-Agentic-2026`, git never
uploads it and never overwrites it. Never paste a key into a notebook cell.

| Key | Used by |
|---|---|
| `OPENAI_API_KEY` | every lab |
| `ANTHROPIC_API_KEY` | Labs 1.1, 1.5 and 1.8 |
| `GEMINI_API_KEY` | Labs 1.1 and 1.5 |
| `GROQ_API_KEY` | Labs 1.1 and 1.3 |
| `LANGSMITH_API_KEY` | Lab 1.3 |

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

- Some labs write working files as they run: `data.csv` and `chat_data.json` in Lab 1.6, and the
  `chroma_banking/` and `banking_faiss_index/` vector stores in Lab 1.7. They are recreated on every run, so
  deleting them is always safe.
- Lab 1.8 downloads a small re-ranking model from Hugging Face the first time it runs.
- Lab 1.6's optional high-resolution PDF cell needs Tesseract OCR and Poppler installed on the machine; every
  other cell runs without them.
- **One expected warning.** Labs 1.6, 1.7 and 1.8 import from `langchain-community`, which LangChain stopped
  maintaining in May 2026. The loaders and vector stores used from it have no maintained replacement yet, so
  the first import prints a `DeprecationWarning`, and the code works as shown.
