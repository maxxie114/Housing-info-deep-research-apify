import json
import os
from typing import Any, Dict, List
from io import BytesIO

import requests
import streamlit as st
from PyPDF2 import PdfReader
try:
    from docx import Document
except ImportError:
    Document = None

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(
    page_title="Building Compliance Consultant",
    page_icon="🏗️",
    layout="wide",
)

# --- Style (Professional compliance-focused design) ---
st.markdown(
    """
    <style>
    :root {
        --accent: #2563eb;
        --success: #22c55e;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg: #0f172a;
        --panel: #1e293b;
        --text: #e2e8f0;
        --muted: #94a3b8;
    }
    body, .main { background: var(--bg); color: var(--text); }
    .stApp { background: radial-gradient(circle at 20% 20%, rgba(37,99,235,0.08), transparent 25%),
                        radial-gradient(circle at 80% 10%, rgba(34,197,94,0.06), transparent 20%),
                        var(--bg); }
    h1, h2, h3 { color: var(--text); }
    .card { background: var(--panel); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 1rem; }
    .pill { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px; background: rgba(255,255,255,0.08); color: var(--muted); font-size: 0.8rem; margin-right: 0.4rem; }
    .trace-item { border-left: 3px solid var(--accent); padding-left: 0.8rem; margin-bottom: 0.8rem; }
    .step-header { font-weight: 600; color: var(--text); }
    .step-desc { color: var(--muted); font-size: 0.95rem; }
    .compliant { color: var(--success); }
    .non-compliant { color: var(--danger); }
    .warning { color: var(--warning); }
    textarea, input, select { background: #0e1528 !important; color: var(--text) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏗️ Building Compliance Consultant")
st.caption("NCC/BCA DTS Assessment · Code Retrieval · Evidence Gathering · Compliance Reporting")

# File upload utility functions
def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PdfReader(BytesIO(pdf_file.read()))
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_docx(docx_file) -> str:
    """Extract text from uploaded DOCX file"""
    if Document is None:
        return "Error: python-docx not installed"
    try:
        doc = Document(BytesIO(docx_file.read()))
        text = ""
        for para_num, para in enumerate(doc.paragraphs):
            if para.text.strip():
                text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"

def extract_text_from_txt(txt_file) -> str:
    """Extract text from uploaded TXT file"""
    try:
        return txt_file.read().decode('utf-8')
    except Exception as e:
        return f"Error extracting TXT: {str(e)}"

# Sidebar for project details and file upload
with st.sidebar:
    st.header("🔧 Configuration")
    api_base = st.text_input("API base", value=API_BASE, help="Backend FastAPI base URL")
    health_status = st.empty()
    
    st.header("📤 Upload Documents")
    st.caption("Upload building documentation (PDF, DOCX, or TXT)")
    
    uploaded_files = st.file_uploader(
        "Upload building plans, specs, or reports",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload project documentation to automatically extract design details"
    )
    
    extracted_text = ""
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        
        with st.expander("📄 View Extracted Text", expanded=False):
            for uploaded_file in uploaded_files:
                st.markdown(f"**{uploaded_file.name}**")
                
                if uploaded_file.name.lower().endswith('.pdf'):
                    file_text = extract_text_from_pdf(uploaded_file)
                elif uploaded_file.name.lower().endswith('.docx'):
                    file_text = extract_text_from_docx(uploaded_file)
                elif uploaded_file.name.lower().endswith('.txt'):
                    file_text = extract_text_from_txt(uploaded_file)
                else:
                    file_text = "Unsupported file type"
                
                extracted_text += f"\n\n=== {uploaded_file.name} ===\n{file_text}\n"
                st.text_area(
                    f"Content from {uploaded_file.name}",
                    file_text[:500] + "..." if len(file_text) > 500 else file_text,
                    height=150,
                    disabled=True,
                    key=f"preview_{uploaded_file.name}"
                )
        
        if st.button("📋 Auto-fill from Uploaded Files"):
            st.session_state['auto_fill_text'] = extracted_text
            st.success("Text extracted! Scroll down to review and submit.")
    
    st.header("📋 Project Classification")
    building_class = st.selectbox(
        "Building Class",
        ["Class 1a", "Class 1b", "Class 2", "Class 3", "Class 5", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10"],
        help="NCC Building Classification"
    )
    
    assessment_scope = st.text_input(
        "Assessment Scope",
        placeholder="e.g., Fire safety and accessibility",
        help="Focus areas for compliance assessment"
    )

# Main input area
col_input, col_meta = st.columns([2, 1])

with col_input:
    # Check if auto-fill text is available
    default_text = st.session_state.get('auto_fill_text', '')
    
    project_description = st.text_area(
        "Project Description",
        value=default_text,
        placeholder="e.g., 3-storey residential apartment building, Type A construction, Victoria. 12 units across 3 levels with basement parking. Total floor area 1,200m². Accessible entrance via ramp from street level.\n\nOr upload documents using the sidebar and click 'Auto-fill from Uploaded Files'.",
        height=200,
        help="Comprehensive project description including size, location, construction type, key features. Or upload PDF/DOCX files in the sidebar."
    )
    
    # Clear auto-fill after use
    if default_text and project_description == default_text:
        if st.button("🗑️ Clear Auto-filled Text"):
            st.session_state['auto_fill_text'] = ''
            st.rerun()
    
    design_details = st.text_area(
        "Design Details (Optional)",
        placeholder="e.g., Fire-rated walls: 90/90/90. Exit stairways: 1000mm width. Accessible toilets on ground floor. Drawing references: DA-01 to DA-15.\n\nThis field auto-populates from uploaded documents.",
        height=100,
        help="Specific design specifications, drawing references, or technical details"
    )
    
    specific_concerns = st.text_input(
        "Specific Concerns (Optional)",
        placeholder="e.g., Stairway dimensions, fire door FRL ratings",
        help="Particular compliance questions or concerns"
    )

with col_meta:
    st.info("**Quick Tips:**\n- Upload PDF/DOCX files in sidebar for auto-extraction\n- Or manually enter project details\n- Specify building class accurately\n- Include key dimensions if known\n- Reference drawings if available")
    
    st.markdown("**📁 Supported File Types:**")
    st.markdown("- PDF (.pdf)\n- Word (.docx)\n- Text (.txt)")
    
    assess_btn = st.button("🔍 Assess Compliance", type="primary", use_container_width=True)


def ping_health(api_base: str) -> bool:
    try:
        url = f"{api_base.rstrip('/')}/health"
        r = requests.get(url, timeout=5)
        return r.status_code == 200
    except Exception:
        return False

status_placeholder = st.empty()

# Show backend connectivity status
if api_base:
    ok = ping_health(api_base)
    if ok:
        health_status.success("✅ Backend connected", icon="✅")
    else:
        health_status.error("⚠️ Backend not reachable", icon="⚠️")


def call_compliance_api(api_base: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{api_base.rstrip('/')}/assess-compliance"
    r = requests.post(url, json=request_data, timeout=300)  # Longer timeout for compliance assessment
    r.raise_for_status()
    return r.json()


def call_compliance_api_with_files(api_base: str, building_class: str, assessment_scope: str, 
                                    project_description: str, design_details: Optional[str], 
                                    specific_concerns: Optional[str], uploaded_files: List) -> Dict[str, Any]:
    """Call the file upload endpoint with multipart form data"""
    url = f"{api_base.rstrip('/')}/assess-compliance-with-files"
    
    # Prepare form data
    data = {
        "building_class": building_class,
        "assessment_scope": assessment_scope,
        "project_description": project_description if project_description else "",
        "design_details": design_details if design_details else "",
        "specific_concerns": specific_concerns if specific_concerns else ""
    }
    
    # Prepare files
    files_payload = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            uploaded_file.seek(0)  # Reset file pointer
            files_payload.append(
                ("files", (uploaded_file.name, uploaded_file.read(), uploaded_file.type))
            )
    
    r = requests.post(url, data=data, files=files_payload if files_payload else None, timeout=300)
    r.raise_for_status()
    return r.json()


def render_compliance_summary(summary: Dict[str, Any]):
    st.subheader("📊 Compliance Summary")
    
    cols = st.columns(4)
    with cols[0]:
        st.metric("✅ Compliant", summary.get("compliant_clauses", 0))
    with cols[1]:
        st.metric("❌ Non-Compliant", summary.get("non_compliant_clauses", 0))
    with cols[2]:
        st.metric("⚡ Performance Solutions", summary.get("performance_solution_required", 0))
    with cols[3]:
        status = summary.get("overall_status", "Unknown")
        if "Compliant" in status and "Non" not in status:
            st.success(status)
        elif "Non-Compliant" in status:
            st.error(status)
        else:
            st.warning(status)


def render_trace(trace: List[Dict[str, Any]]):
    st.subheader("🔄 Assessment Process")
    if not trace:
        st.write("No trace available.")
        return
    
    # Show only key steps to avoid clutter
    key_steps = [t for t in trace if t.get("type") in ["ai", "tool"] and t.get("tool_calls") or t.get("tool_name")]
    
    for item in key_steps[:15]:  # Limit to first 15 key steps
        t = item.get("type")
        with st.container():
            st.markdown("<div class='trace-item'>", unsafe_allow_html=True)
            st.markdown(f"**Step {item.get('message_index', '?')} · {t}**", unsafe_allow_html=True)
            if item.get("tool_calls"):
                for tc in item["tool_calls"]:
                    tool_name = tc.get('name', 'unknown')
                    if 'dts-assessment' in tool_name:
                        st.markdown(f"<div class='step-desc'>📜 Code Retrieval: {tool_name}</div>", unsafe_allow_html=True)
                    elif 'evidence-gathering' in tool_name:
                        st.markdown(f"<div class='step-desc'>📋 Evidence Check: {tool_name}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='step-desc'>🔧 {tool_name}</div>", unsafe_allow_html=True)
            if item.get("tool_name"):
                st.markdown(f"<div class='step-desc'>🔧 {item.get('tool_name')}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


def render_files(files: Dict[str, Any]):
    if not files:
        return
    st.subheader("📄 Generated Reports")
    
    # Prioritize compliance reports
    priority_order = ["compliance_report.md", "non_compliance_summary.md", "evidence_checklist.md"]
    sorted_files = sorted(files.keys(), key=lambda x: priority_order.index(x) if x in priority_order else 999)
    
    for path in sorted_files:
        content = files[path]
        file_icon = "📋" if "compliance" in path.lower() else "📄"
        expanded = path in priority_order[:2]  # Auto-expand main compliance reports
        
        with st.expander(f"{file_icon} {path}", expanded=expanded):
            st.markdown(content)


if assess_btn and project_description.strip():
    if not building_class or not assessment_scope:
        status_placeholder.warning("Please specify Building Class and Assessment Scope in the sidebar.", icon="⚠️")
    else:
        status_placeholder.info("🔄 Conducting compliance assessment... This may take 1-2 minutes.", icon="⏳")
        
        try:
            # Use file upload endpoint if files were uploaded
            if uploaded_files:
                result = call_compliance_api_with_files(
                    api_base, 
                    building_class, 
                    assessment_scope,
                    project_description,
                    design_details,
                    specific_concerns,
                    uploaded_files
                )
            else:
                # Use standard JSON endpoint
                request_data = {
                    "project_description": project_description.strip(),
                    "building_class": building_class,
                    "assessment_scope": assessment_scope.strip(),
                    "design_details": design_details.strip() if design_details else None,
                    "specific_concerns": specific_concerns.strip() if specific_concerns else None
                }
                result = call_compliance_api(api_base, request_data)
            
            success = result.get("success", False)
            final_response = result.get("final_response", "")
            trace = result.get("execution_trace", [])
            files = result.get("files", {})
            compliance_summary = result.get("compliance_summary")

            if success:
                status_placeholder.success("✅ Compliance assessment complete!", icon="✅")
                
                # Display compliance summary if available
                if compliance_summary:
                    render_compliance_summary(compliance_summary)
                
                # Main response
                st.subheader("📝 Executive Summary")
                st.markdown(final_response or "(No summary generated)")
                
                # Generated files
                render_files(files)
                
                # Process trace
                with st.expander("🔍 View Assessment Process", expanded=False):
                    render_trace(trace)
            else:
                status_placeholder.error("❌ Assessment failed", icon="❌")
                st.error(final_response or "Unknown error")
                
        except Exception as e:
            status_placeholder.error(f"❌ Error: {e}", icon="❌")
            st.exception(e)
else:
    if not project_description.strip() and assess_btn:
        status_placeholder.warning("Please provide a project description.", icon="💡")
    else:
        status_placeholder.info("Enter project details and click 'Assess Compliance' to begin NCC/BCA DTS assessment.", icon="💡")
