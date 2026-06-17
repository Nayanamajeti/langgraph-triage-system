# app.py — Multi-Agent Triage Streamlit demo

import os
from functools import lru_cache

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from config import DOMAIN_CONFIGS
from graph import build_triage_graph

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Triage",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Domain metadata (UI only) ─────────────────────────────────
DOMAIN_META = {
    "Healthcare": {
        "icon": "🩺",
        "tagline": "Clinical symptom intake & severity classification",
        "sample": {
            "patient_name": "Jane Doe",
            "age": 42,
            "symptoms": "Persistent headache with blurred vision for 2 days, mild nausea",
            "duration": "2 days",
            "pain_scale": 6,
            "medical_history": "Migraine history, no known drug allergies",
        },
    },
    "IT Helpdesk": {
        "icon": "💻",
        "tagline": "Incident reporting & priority triage",
        "sample": {
            "reporter_name": "Alex Chen",
            "issue_title": "Email service unavailable",
            "description": "Users cannot send or receive emails since 9 AM. Outlook shows connection errors.",
            "system_affected": "Microsoft Exchange / Outlook",
            "error_message": "Cannot connect to server. Error 0x800CCC0E",
            "users_affected": 120,
            "business_impact": "Sales team unable to contact clients",
        },
    },
    "HR Support": {
        "icon": "👥",
        "tagline": "Employee case intake & escalation routing",
        "sample": {
            "employee_name": "Sam Rivera",
            "department": "Engineering",
            "issue_type": "Workplace concern",
            "description": "Request for guidance on flexible working policy after team restructure",
            "employees_affected": 1,
            "date_of_incident": "2026-06-10",
        },
    },
}

SEVERITY_STYLE = {
    "Emergency": {"color": "#DC2626", "bg": "#FEF2F2", "border": "#FECACA", "emoji": "🔴"},
    "Urgent": {"color": "#D97706", "bg": "#FFFBEB", "border": "#FDE68A", "emoji": "🟡"},
    "Routine": {"color": "#059669", "bg": "#ECFDF5", "border": "#A7F3D0", "emoji": "🟢"},
}

PIPELINE_STEPS = [
    ("Intake", "Structured form → summary"),
    ("Triage", "AI severity classification"),
    ("Router", "Emergency vs standard path"),
    ("RAG / Alert", "Guidelines or immediate actions"),
    ("Report", "Final structured output"),
]


# ── Custom styling ────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0F766E 0%, #0D9488 50%, #14B8A6 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 24px rgba(13, 148, 136, 0.25);
    }
    .main-header h1 {
        color: #FFFFFF !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        letter-spacing: -0.02em;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.9) !important;
        margin: 0.5rem 0 0 0 !important;
        font-size: 1.05rem;
    }
    .badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    .pipeline-step {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
    }
    .pipeline-step strong { color: #0F766E; }
    .pipeline-step span { color: #64748B; }
    .disclaimer {
        background: #FFF7ED;
        border-left: 4px solid #F97316;
        padding: 0.85rem 1rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.85rem;
        color: #9A3412;
        margin-bottom: 1rem;
    }
    div[data-testid="stForm"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0F766E, #0D9488) !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        border-radius: 8px !important;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


@lru_cache(maxsize=1)
def get_graph():
    return build_triage_graph()


def render_header():
    st.markdown(
        """
        <div class="main-header">
            <h1>Multi-Agent Triage</h1>
            <p>Multi-agent intake &amp; triage — powered by LangGraph + Gemini</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_severity_badge(severity: str, label: str):
    style = SEVERITY_STYLE.get(severity, SEVERITY_STYLE["Urgent"])
    st.markdown(
        f"""
        <div style="
            background:{style['bg']};
            border:1px solid {style['border']};
            border-radius:12px;
            padding:1.25rem 1.5rem;
            margin-bottom:1rem;
        ">
            <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.5rem;">
                <span style="font-size:1.5rem;">{style['emoji']}</span>
                <span style="
                    color:{style['color']};
                    font-size:1.35rem;
                    font-weight:700;
                ">{severity}</span>
            </div>
            <p style="margin:0;color:#475569;font-size:0.95rem;">{label}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_form_field(field: dict, domain: str, key_prefix: str):
    """Render a single intake field based on domain config."""
    key = field["key"]
    label = field["label"]
    ftype = field["type"]
    widget_key = f"{key_prefix}_{key}"

    if ftype == "text":
        return st.text_input(label, key=widget_key)
    if ftype == "number":
        return st.number_input(label, min_value=0, step=1, key=widget_key)
    if ftype == "textarea":
        return st.text_area(label, height=120, key=widget_key)
    if ftype == "slider":
        return st.slider(label, min_value=1, max_value=10, value=5, key=widget_key)
    return st.text_input(label, key=widget_key)


def fill_sample_data(domain: str, key_prefix: str):
    sample = DOMAIN_META[domain]["sample"]
    for field in DOMAIN_CONFIGS[domain]["intake_fields"]:
        key = field["key"]
        if key in sample:
            st.session_state[f"{key_prefix}_{key}"] = sample[key]


def clear_form_data(domain: str, key_prefix: str):
    for field in DOMAIN_CONFIGS[domain]["intake_fields"]:
        wk = f"{key_prefix}_{field['key']}"
        if field["type"] == "number":
            st.session_state[wk] = 0
        elif field["type"] == "slider":
            st.session_state[wk] = 5
        else:
            st.session_state[wk] = ""


def reset_to_form(domain: str, key_prefix: str):
    """Clear results and reset form so the user can start a new case."""
    if "last_result" in st.session_state:
        del st.session_state["last_result"]
    if "last_domain" in st.session_state:
        del st.session_state["last_domain"]
    clear_form_data(domain, key_prefix)


def render_results(result: dict, domain: str, key_prefix: str):
    config = DOMAIN_CONFIGS[domain]
    severity = result.get("severity", "Urgent")
    severity_label = config["severity_levels"].get(severity, severity)

    st.markdown("### Triage Results")

    action_col1, action_col2 = st.columns([2, 1])
    with action_col1:
        st.caption("Review the assessment below, or start a new case.")
    with action_col2:
        if st.button("Run another case", type="primary", use_container_width=True, key="reset_top"):
            reset_to_form(domain, key_prefix)
            st.rerun()

    render_severity_badge(severity, severity_label)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Classification reasoning**")
        st.info(result.get("triage_reasoning", "—"))
    with col_b:
        red_flags = result.get("red_flags") or []
        st.markdown("**Red flags / critical indicators**")
        if red_flags:
            for flag in red_flags:
                st.warning(f"⚠️ {flag}")
        else:
            st.success("No critical indicators flagged")

    if result.get("skip_rag"):
        with st.expander("Emergency actions (RAG bypassed)", expanded=True):
            st.markdown(result.get("immediate_actions", ""))
    else:
        with st.expander("Guideline recommendations", expanded=False):
            st.markdown(result.get("rag_recommendations", "—"))
        with st.expander("Retrieved context", expanded=False):
            st.caption(result.get("rag_context", "—"))

    st.markdown("---")
    st.markdown(f"### {config['report_title']}")
    report_text = result.get("final_report", "No report generated.")
    st.markdown(report_text)

    st.download_button(
        label="Download report",
        data=report_text,
        file_name=f"multi_agent_triage_{domain.lower().replace(' ', '_')}_report.md",
        mime="text/markdown",
        use_container_width=True,
        key="download_report",
    )

    st.markdown("")
    if st.button("← Back to form", use_container_width=True, key="reset_bottom"):
        reset_to_form(domain, key_prefix)
        st.rerun()


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Configuration")
    domain = st.selectbox(
        "Domain",
        list(DOMAIN_CONFIGS.keys()),
        format_func=lambda d: f"{DOMAIN_META[d]['icon']}  {d}",
    )
    meta = DOMAIN_META[domain]
    st.caption(meta["tagline"])

    st.markdown("---")
    st.markdown("### Agent pipeline")
    for i, (name, desc) in enumerate(PIPELINE_STEPS, 1):
        st.markdown(
            f'<div class="pipeline-step"><strong>{i}. {name}</strong><br>'
            f'<span>{desc}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### Severity levels")
    for level, label in DOMAIN_CONFIGS[domain]["severity_levels"].items():
        st.caption(label)

    st.markdown("---")
    api_ok = bool(os.getenv("GOOGLE_API_KEY"))
    if api_ok:
        st.success("API key configured")
    else:
        st.error("GOOGLE_API_KEY missing — add to Secrets")

# ── Main layout ───────────────────────────────────────────────
render_header()

if domain == "Healthcare":
    st.markdown(
        '<div class="disclaimer">'
        "<strong>Demo only.</strong> Multi-Agent Triage is not a medical device and does not "
        "replace professional clinical judgment. In a real emergency, call your local "
        "emergency number immediately."
        "</div>",
        unsafe_allow_html=True,
    )

left, right = st.columns([3, 2], gap="large")

FORM_PREFIX = f"form_{domain.replace(' ', '_')}"

with left:
    st.markdown(f"#### {meta['icon']} Intake Form")
    st.caption(f"Complete the fields below for **{domain}** triage.")

    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        if st.button("Load sample case", use_container_width=True):
            fill_sample_data(domain, FORM_PREFIX)
            st.rerun()
    with btn_col2:
        if st.button("Clear form", use_container_width=True):
            clear_form_data(domain, FORM_PREFIX)
            if "last_result" in st.session_state:
                del st.session_state["last_result"]
            st.rerun()

    with st.form("intake_form", clear_on_submit=False):
        form_data = {}
        fields = DOMAIN_CONFIGS[domain]["intake_fields"]

        # Two-column layout for shorter fields
        i = 0
        while i < len(fields):
            f1 = fields[i]
            if f1["type"] in ("textarea", "slider") or i + 1 >= len(fields):
                form_data[f1["key"]] = render_form_field(f1, domain, FORM_PREFIX)
                i += 1
            else:
                f2 = fields[i + 1]
                if f2["type"] in ("textarea", "slider"):
                    form_data[f1["key"]] = render_form_field(f1, domain, FORM_PREFIX)
                    i += 1
                else:
                    c1, c2 = st.columns(2)
                    with c1:
                        form_data[f1["key"]] = render_form_field(f1, domain, FORM_PREFIX)
                    with c2:
                        form_data[f2["key"]] = render_form_field(f2, domain, FORM_PREFIX)
                    i += 2

        submitted = st.form_submit_button(
            "Run triage pipeline",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        # Validate required textarea fields
        missing = []
        for field in fields:
            if field["type"] == "textarea" and not form_data.get(field["key"], "").strip():
                missing.append(field["label"])
        if missing:
            st.error(f"Please complete: {', '.join(missing)}")
        elif not os.getenv("GOOGLE_API_KEY"):
            st.error("Set GOOGLE_API_KEY in your environment or Streamlit Secrets.")
        else:
            with st.spinner("Running multi-agent pipeline…"):
                try:
                    graph = get_graph()
                    result = graph.invoke({
                        "domain": domain,
                        "domain_config": DOMAIN_CONFIGS[domain],
                        "form_data": form_data,
                    })
                    st.session_state["last_result"] = result
                    st.session_state["last_domain"] = domain
                except Exception as exc:
                    st.error(f"Pipeline error: {exc}")

with right:
    st.markdown("#### How it works")
    st.markdown(
        """
        1. **Intake** formats your form into a structured summary  
        2. **Triage** classifies severity with Gemini  
        3. **Router** sends emergencies to the alert path  
        4. **RAG** retrieves domain guidelines (when available)  
        5. **Report** produces a final summary for review  
        """
    )

    if (
        "last_result" in st.session_state
        and st.session_state.get("last_domain") == domain
    ):
        result = st.session_state["last_result"]
        severity = result.get("severity", "—")
        style = SEVERITY_STYLE.get(severity, {})
        st.markdown(
            f'<div class="pipeline-step" style="text-align:center;">'
            f'<strong>Last run</strong><br>'
            f'<span style="font-size:1.25rem;">{style.get("emoji", "")} {severity}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )

# ── Results section ───────────────────────────────────────────
if (
    "last_result" in st.session_state
    and st.session_state.get("last_domain") == domain
):
    st.markdown("---")
    render_results(st.session_state["last_result"], domain, FORM_PREFIX)
