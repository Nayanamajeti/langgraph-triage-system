🏥 Multi-Agent Triage System
---
> Domain-agnostic intake & triage powered by LangGraph multi-agent architecture — supports Healthcare, IT Helpdesk, and HR with conditional routing and RAG-backed recommendations.
> 
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-blueviolet?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-green?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-1.5--flash-orange?style=flat-square&logo=google)
![FAISS](https://img.shields.io/badge/FAISS-Vector--Store-purple?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=flat-square&logo=streamlit)
---
🧠 What Is langgraph triage system ?
---

Most AI triage tools are single-domain chatbots with a fixed prompt. TriageIQ is different.
It's a stateful multi-agent system built with LangGraph — where specialised agents hand off to each other like a real workflow, with conditional routing that dynamically changes the pipeline based on severity. A chest-pain emergency takes a completely different path than a routine appointment request. An IT outage routes differently than a cosmetic UI bug.
Built as a domain-agnostic architecture — the same agent graph powers Healthcare triage, IT incident management, and HR case handling. Switch domains in one dropdown. No code changes needed.

---
✨ Features
---
Five agents each with a single responsibility:
Intake Agent — structures raw form data into a clean case summary
Triage Agent — classifies severity using domain-specific prompts via Gemini
Router — conditional edge that sends emergencies down the alert path, others to RAG
Alert Agent — for emergencies only; bypasses RAG for immediate action instructions
RAG Agent — retrieves relevant guidelines from a FAISS knowledge base
Report Agent — synthesizes everything into a structured professional report
🔀 Conditional Routing (The Core Innovation)
LangGraph's conditional edges mean the pipeline is not linear — it branches based on severity:
```
Emergency  → Alert Agent → Report Agent   (fast path, no RAG)
Urgent     → RAG Agent   → Report Agent   (guidelines retrieved)
Routine    → RAG Agent   → Report Agent   (guidelines retrieved)
```
🌐 Domain-Agnostic by Design
---

One config file drives three completely different domains:
Domain	Severity Scale	Use Case
🏥 Healthcare	Emergency / Urgent / Routine	Patient symptom triage
💻 IT Helpdesk	P1 Critical / P2 High / P3 Medium	Incident prioritisation
👥 HR Support	Immediate / This Week / Backlog	HR case management
📋 Structured Output
Every case produces:
Colour-coded severity badge (🔴 🟡 🟢)
Classification reasoning from the Triage Agent
Red flags / critical indicators grid
RAG-retrieved guideline recommendations
Full structured case report with 5 sections

---
🏗️ Architecture
---
Agent Graph
```
                    START
                      │
                      ▼
            ┌─────────────────┐
            │  INTAKE AGENT   │
            │ Form → Summary  │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  TRIAGE AGENT   │
            │ Gemini classifies│
            │ severity via    │
            │ domain prompt   │
            └────────┬────────┘
                     │
           ┌─────────┴──────────┐
           │   CONDITIONAL      │
           │     ROUTER         │
           └──────┬─────────────┘
                  │
       ┌──────────┴──────────┐
       │ Emergency            │ Urgent / Routine
       ▼                      ▼
┌────────────┐      ┌──────────────────┐
│ALERT AGENT │      │    RAG AGENT     │
│Immediate   │      │ FAISS retrieval  │
│actions,    │      │ + Gemini recs    │
│no RAG      │      └────────┬─────────┘
└─────┬──────┘               │
      └──────────┬───────────┘
                 ▼
        ┌─────────────────┐
        │  REPORT AGENT   │
        │ Final structured│
        │ case report     │
        └────────┬────────┘
                 │
                END
```
🚀 Getting Started
---
Prerequisites
Python 3.10+
Free Google Gemini API key → Get one here
Installation
```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/langgraph-triage-system

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt
```
Configure API Key
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```
> ⚠️ Never commit your `.env` file. It's already in `.gitignore`.
Run the App
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.
Test the Agent Graph (Terminal)
```bash
python graph.py
```
Runs a sample healthcare emergency case and prints each agent's output to the terminal — useful for debugging the pipeline without the UI.
---
📁 Project Structure
```
triageiq/
│
├── app.py              # Streamlit UI — form, results, domain switcher
├── graph.py            # LangGraph graph definition — nodes, edges, routing
├── agents.py           # All 5 agent functions (intake, triage, alert, rag, report)
├── config.py           # Domain configs — prompts, fields, severity labels
├── ingest.py           # PDF ingestion → FAISS index (for RAG knowledge base)
│
├── data/
│   └── guidelines/     # Drop domain PDFs here (gitignored)
├── faiss_index_*/      # Auto-generated FAISS indexes per domain (gitignored)
│
├── .env                # API key (gitignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---
🧰 Tech Stack
---

Component	Technology
Agent Orchestration	LangGraph (StateGraph with conditional edges)
LLM	Google Gemini 1.5 Flash
RAG Embeddings	HuggingFace `all-MiniLM-L6-v2`
Vector Store	FAISS
RAG Framework	LangChain
UI	Streamlit
Environment	python-dotenv

💡 Example Outputs
---
🔴 Healthcare Emergency
---
Input: 55-year-old, severe chest pain radiating to left arm, pain scale 9/10, shortness of breath, 30 minutes duration
Triage Agent: `Emergency`
Reasoning: Classic ACS presentation — chest pain + radiation + diaphoresis + dyspnea
Route taken: Intake → Triage → Alert Agent → Report (RAG bypassed for speed)
Report includes: Immediate 911 guidance, what not to do, cardiac risk assessment

---
🟢 IT Helpdesk Routine
---
Input: Cosmetic UI display issue on HR portal, 1 user affected, no error message
Triage Agent: `P3 Medium — Routine`
Reasoning: Cosmetic issue with no functional impact or productivity loss
Route taken: Intake → Triage → RAG Agent → Report (Standard queue, guidelines retrieved)

---
🔬 What Makes This Novel
---
Unlike single-agent LLM tools, TriageIQ introduces:
Stateful multi-agent orchestration — LangGraph StateGraph with shared TypedDict state passed between agents
Conditional routing — Emergency cases take a completely different execution path, not just a different prompt
Config-driven domain switching — entire agent behaviour (prompts, fields, severity labels) driven by a single config dict, not hardcoded logic
RAG-augmented recommendations — domain knowledge base integrated into the pipeline via FAISS + HuggingFace embeddings
Graceful RAG fallback — if no knowledge base is uploaded, agents fall back to LLM parametric knowledge without breaking

---
⚠️ Disclaimer
---
TriageIQ is a demonstration project built to explore applied LLM engineering with LangGraph. It is not a certified medical device and does not replace professional clinical, IT, or HR judgment. In a real emergency, contact the appropriate emergency services immediately.

---
👩‍💻 Author
Nayana Majeti
B.Tech — AI & ML | Vishwakarma Institute of Technology, Pune.

---
📄 License
MIT License — feel free to use, modify, and build on top of this.
---
> *Built as part of a personal initiative to explore applied LLM engineering — specifically stateful multi-agent systems and real-world agentic workflows using LangGraph.*
