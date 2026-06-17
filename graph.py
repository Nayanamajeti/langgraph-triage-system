# graph.py
from dotenv import load_dotenv
load_dotenv(override=True)
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List
from agents import (
    intake_agent,
    triage_agent,
    route_by_severity,
    alert_agent,
    rag_agent,
    report_agent
)

# ── Define State Schema ──────────────────────────────────────
# This is the shared dictionary all agents read from and write to
class TriageState(TypedDict):
    # Inputs
    domain: str
    domain_config: dict
    form_data: dict

    # Agent outputs (filled progressively)
    intake_summary: Optional[str]
    severity: Optional[str]
    triage_reasoning: Optional[str]
    red_flags: Optional[List[str]]
    rag_context: Optional[str]
    rag_recommendations: Optional[str]
    immediate_actions: Optional[str]
    skip_rag: Optional[bool]
    final_report: Optional[str]


# ── Build The Graph ──────────────────────────────────────────
def build_triage_graph():
    # Create graph with our state schema
    graph = StateGraph(TriageState)

    # Add all nodes (agent name → agent function)
    graph.add_node("intake_agent", intake_agent)
    graph.add_node("triage_agent", triage_agent)
    graph.add_node("alert_agent", alert_agent)
    graph.add_node("rag_agent", rag_agent)
    graph.add_node("report_agent", report_agent)

    # Add normal edges (always go A → B)
    graph.add_edge("intake_agent", "triage_agent")
    graph.add_edge("alert_agent", "report_agent")
    graph.add_edge("rag_agent", "report_agent")
    graph.add_edge("report_agent", END)

    # Add conditional edge (triage → alert OR rag based on severity)
    graph.add_conditional_edges(
        "triage_agent",       # FROM triage
        route_by_severity,    # CALL this to decide
        {
            "alert_agent": "alert_agent",
            "rag_agent": "rag_agent"
        }
    )

    # Set entry point
    graph.set_entry_point("intake_agent")

    # Compile and return
    return graph.compile()


# ── Quick Terminal Test ──────────────────────────────────────
if __name__ == "__main__":
    from config import DOMAIN_CONFIGS

    triage_graph = build_triage_graph()

    # Test with a healthcare emergency case
    test_input = {
        "domain": "Healthcare",
        "domain_config": DOMAIN_CONFIGS["Healthcare"],
        "form_data": {
            "patient_name": "Test Patient",
            "age": 55,
            "symptoms": "severe chest pain radiating to left arm, sweating, shortness of breath",
            "duration": "30 minutes",
            "pain_scale": 9,
            "medical_history": "hypertension, previous smoker"
        }
    }

    print("\n" + "="*50)
    print("RUNNING TRIAGE GRAPH...")
    print("="*50 + "\n")

    result = triage_graph.invoke(test_input)

    print("\n" + "="*50)
    print(f"SEVERITY: {result['severity']}")
    print(f"REASONING: {result['triage_reasoning']}")
    print("\nFINAL REPORT:")
    print(result['final_report'])