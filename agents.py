# agents.py

import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Check your .env file.")

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.2,
    )

# ── AGENT 1: Intake ─────────────────────────────────────────
def intake_agent(state: dict) -> dict:
    """
    Formats raw form data into a clean summary string.
    No LLM call needed — pure formatting.
    """
    domain_config = state["domain_config"]
    form_data = state["form_data"]

    # Build a readable intake summary
    intake_summary = ""
    for field in domain_config["intake_fields"]:
        key = field["key"]
        label = field["label"]
        value = form_data.get(key, "Not provided")
        intake_summary += f"{label}: {value}\n"

    print(f"[INTAKE AGENT] Processed intake data")
    return {"intake_summary": intake_summary}


# ── AGENT 2: Triage ─────────────────────────────────────────
def triage_agent(state: dict) -> dict:
    """
    Classifies severity using domain-specific triage prompt.
    Returns severity level + reasoning + red flags.
    """
    llm = get_llm()
    domain_config = state["domain_config"]
    intake_summary = state["intake_summary"]

    # Build the triage prompt using domain config
    prompt = domain_config["triage_prompt"].format(
        intake_data=intake_summary
    )

    print(f"[TRIAGE AGENT] Classifying severity...")
    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        # Clean and parse JSON response
        raw = response.content.strip()
        # Remove markdown code blocks if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        triage_result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        triage_result = {
            "severity": "Urgent",
            "reasoning": "Could not parse triage response — defaulting to Urgent",
            "red_flags": []
        }

    print(f"[TRIAGE AGENT] Severity: {triage_result['severity']}")
    return {
        "severity": triage_result["severity"],
        "triage_reasoning": triage_result["reasoning"],
        "red_flags": triage_result.get("red_flags", [])
    }


# ── ROUTER: Conditional Edge Function ───────────────────────
def route_by_severity(state: dict) -> str:
    """
    This is the conditional edge function.
    LangGraph calls this to decide which node to go to next.
    Returns the name of the next node.
    """
    severity = state.get("severity", "Urgent")
    if severity == "Emergency":
        return "alert_agent"
    else:
        return "rag_agent"


# ── AGENT 3A: Alert (Emergency path only) ───────────────────
def alert_agent(state: dict) -> dict:
    """
    For emergencies — skips RAG entirely.
    Generates immediate action instructions.
    """
    llm = get_llm()
    domain = state["domain"]
    intake_summary = state["intake_summary"]
    red_flags = state.get("red_flags", [])

    prompt = f"""
    This is a {domain} EMERGENCY case. Generate immediate action 
    instructions — no time for detailed analysis.
    
    Case Summary: {intake_summary}
    Critical Indicators: {', '.join(red_flags)}
    
    Provide:
    1. Immediate actions to take RIGHT NOW (3-5 bullet points)
    2. Who to contact immediately
    3. What NOT to do
    
    Be direct and urgent in tone.
    """

    print(f"[ALERT AGENT] Generating emergency response...")
    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        "rag_context": "EMERGENCY — RAG bypassed for speed",
        "immediate_actions": response.content,
        "skip_rag": True
    }


# ── AGENT 3B: RAG (Urgent/Routine path) ─────────────────────
def rag_agent(state: dict) -> dict:
    """
    Searches the knowledge base for relevant guidelines/docs.
    Falls back gracefully if no knowledge base is indexed.
    """
    domain_config = state["domain_config"]
    form_data = state["form_data"]
    severity = state["severity"]

    # Get primary complaint field
    # Works for any domain — finds first textarea field value
    primary_issue = ""
    for field in domain_config["intake_fields"]:
        if field["type"] == "textarea":
            primary_issue = form_data.get(field["key"], "")
            break

    # Try to load FAISS index if it exists
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS

        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        kb_name = domain_config["knowledge_base"]
        index_path = f"faiss_index_{kb_name}"

        if os.path.exists(index_path):
            vectorstore = FAISS.load_local(
                index_path,
                embeddings,
                allow_dangerous_deserialization=True
            )
            docs = vectorstore.similarity_search(primary_issue, k=3)
            context = "\n\n".join([d.page_content for d in docs])
            print(f"[RAG AGENT] Found {len(docs)} relevant chunks")
        else:
            context = "No knowledge base uploaded for this domain."
            print(f"[RAG AGENT] No index found — using LLM knowledge only")

    except Exception as e:
        context = f"Knowledge base unavailable: {str(e)}"
        print(f"[RAG AGENT] Error loading index: {e}")

    # Generate RAG-based recommendations
    llm = get_llm()
    prompt = domain_config["rag_prompt"].format(
        symptoms=primary_issue,
        severity=severity,
        context=context
    )

    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        "rag_context": context,
        "rag_recommendations": response.content
    }


# ── AGENT 4: Report ─────────────────────────────────────────
def report_agent(state: dict) -> dict:
    """
    Final agent — synthesizes everything into a structured report.
    Works for both emergency (uses immediate_actions) and 
    standard (uses rag_recommendations) paths.
    """
    llm = get_llm()
    domain_config = state["domain_config"]
    domain = state["domain"]
    intake_summary = state["intake_summary"]
    severity = state["severity"]
    reasoning = state.get("triage_reasoning", "")
    red_flags = state.get("red_flags", [])

    # Use correct content based on which path was taken
    if state.get("skip_rag"):
        recommendations = state.get("immediate_actions", "")
    else:
        recommendations = state.get("rag_recommendations", "")

    prompt = f"""
    Generate a professional {domain_config['report_title']} based on 
    this case. Format it clearly with sections.
    
    CASE SUMMARY:
    {intake_summary}
    
    TRIAGE RESULT: {severity}
    REASONING: {reasoning}
    RED FLAGS: {', '.join(red_flags) if red_flags else 'None identified'}
    
    RECOMMENDATIONS:
    {recommendations}
    
    Structure the report with these sections:
    ## Case Overview
    ## Severity Assessment  
    ## Key Concerns
    ## Recommended Actions
    ## Next Steps
    
    Be professional, specific, and actionable.
    """

    print(f"[REPORT AGENT] Generating final report...")
    response = llm.invoke([HumanMessage(content=prompt)])

    return {"final_report": response.content}