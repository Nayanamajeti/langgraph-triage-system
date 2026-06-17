# config.py

DOMAIN_CONFIGS = {
    "Healthcare": {
        "intake_fields": [
            {"key": "patient_name", "label": "Patient Name", "type": "text"},
            {"key": "age", "label": "Age", "type": "number"},
            {"key": "symptoms", "label": "Primary Symptoms", "type": "textarea"},
            {"key": "duration", "label": "How long have symptoms persisted?", "type": "text"},
            {"key": "pain_scale", "label": "Pain Scale (1-10)", "type": "slider"},
            {"key": "medical_history", "label": "Relevant Medical History", "type": "textarea"},
        ],
        "severity_levels": {
            "Emergency": "🔴 EMERGENCY — Immediate medical attention required",
            "Urgent": "🟡 URGENT — Needs attention within 2-4 hours",
            "Routine": "🟢 ROUTINE — Schedule a standard appointment"
        },
        "triage_prompt": """You are an experienced medical triage nurse.
Based on the patient information below, classify the severity as exactly 
one of: Emergency, Urgent, or Routine.

Emergency = life-threatening, chest pain, stroke symptoms, severe breathing difficulty
Urgent = significant pain, high fever, injury needing prompt care
Routine = mild symptoms, follow-ups, non-urgent concerns

Patient Info:
{intake_data}

Respond in this exact JSON format:
{{
    "severity": "Emergency|Urgent|Routine",
    "reasoning": "one sentence explaining why",
    "red_flags": ["list", "of", "concerning", "symptoms"] 
}}""",
        "rag_prompt": """You are a clinical guidelines assistant.
Based on these medical guidelines and the patient's symptoms, provide 
relevant treatment protocols and recommended next steps.

Patient symptoms: {symptoms}
Severity: {severity}

Relevant Guidelines:
{context}

Provide specific, actionable clinical recommendations.""",
        "report_title": "Clinical Triage Report",
        "knowledge_base": "healthcare"
    },

    "IT Helpdesk": {
        "intake_fields": [
            {"key": "reporter_name", "label": "Reporter Name", "type": "text"},
            {"key": "issue_title", "label": "Issue Title", "type": "text"},
            {"key": "description", "label": "Issue Description", "type": "textarea"},
            {"key": "system_affected", "label": "System / Application Affected", "type": "text"},
            {"key": "error_message", "label": "Error Message (if any)", "type": "textarea"},
            {"key": "users_affected", "label": "Number of Users Affected", "type": "number"},
            {"key": "business_impact", "label": "Business Impact", "type": "text"},
        ],
        "severity_levels": {
            "Emergency": "🔴 P1 CRITICAL — System down, immediate response",
            "Urgent": "🟡 P2 HIGH — Major impact, respond within 2 hours",
            "Routine": "🟢 P3 MEDIUM — Limited impact, standard queue"
        },
        "triage_prompt": """You are an experienced IT incident manager.
Based on the ticket below, classify priority as exactly one of: 
Emergency, Urgent, or Routine.

Emergency = full system outage, security breach, data loss
Urgent = major feature broken, many users affected
Routine = minor bug, single user issue, enhancement request

Ticket Info:
{intake_data}

Respond in this exact JSON format:
{{
    "severity": "Emergency|Urgent|Routine",
    "reasoning": "one sentence explaining why",
    "red_flags": ["list", "of", "critical", "indicators"]
}}""",
        "rag_prompt": """You are an IT runbook assistant.
Based on available documentation and the incident details, suggest 
resolution steps and escalation procedures.

Issue: {symptoms}
Priority: {severity}

Relevant Documentation:
{context}

Provide specific troubleshooting steps in order.""",
        "report_title": "IT Incident Report",
        "knowledge_base": "it_helpdesk"
    },

    "HR Support": {
        "intake_fields": [
            {"key": "employee_name", "label": "Employee Name", "type": "text"},
            {"key": "department", "label": "Department", "type": "text"},
            {"key": "issue_type", "label": "Issue Type", "type": "text"},
            {"key": "description", "label": "Issue Description", "type": "textarea"},
            {"key": "employees_affected", "label": "Number of Employees Affected", "type": "number"},
            {"key": "date_of_incident", "label": "Date of Incident", "type": "text"},
        ],
        "severity_levels": {
            "Emergency": "🔴 IMMEDIATE — Legal/compliance risk, escalate now",
            "Urgent": "🟡 THIS WEEK — Significant employee impact",
            "Routine": "🟢 STANDARD — Process through normal HR queue"
        },
        "triage_prompt": """You are a senior HR business partner.
Based on the HR case below, classify urgency as exactly one of: 
Emergency, Urgent, or Routine.

Emergency = harassment, discrimination, legal threat, safety issue
Urgent = policy violation, team conflict, performance crisis
Routine = benefits query, policy question, training request

Case Info:
{intake_data}

Respond in this exact JSON format:
{{
    "severity": "Emergency|Urgent|Routine",
    "reasoning": "one sentence explaining why",
    "red_flags": ["list", "of", "serious", "indicators"]
}}""",
        "rag_prompt": """You are an HR policy assistant.
Based on company policies and the case details, recommend the 
appropriate HR response and process.

Issue: {symptoms}
Urgency: {severity}

Relevant Policies:
{context}

Provide specific recommended actions and escalation path.""",
        "report_title": "HR Case Summary",
        "knowledge_base": "hr_support"
    }
}