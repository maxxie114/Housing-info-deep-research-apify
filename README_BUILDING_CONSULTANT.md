# Building Consultant Deep Agent

AI-powered building code compliance assistant specializing in Australian NCC/BCA Deemed-to-Satisfy (DTS) assessment, clause interpretation, and compliance reporting.

## Overview

This intelligent agent assists building professionals by automating the tedious process of NCC/BCA code compliance checking. It retrieves relevant clauses, assesses designs against Deemed-to-Satisfy provisions, gathers evidence, and generates comprehensive compliance reports.

## Features

- 🏗️ **NCC/BCA Code Retrieval** - Access and interpret Australian building code clauses
- ✅ **DTS Compliance Assessment** - Automated Deemed-to-Satisfy requirement checking  
- 📋 **Evidence Gathering** - Systematic collection of design documentation and specifications
- 📊 **Clause-by-Clause Analysis** - Detailed comparison of design against code requirements
- 📝 **Compliance Report Generation** - Professional reports for architects, engineers, certifiers, and builders
- 🚨 **Non-Compliance Detection** - Identification of code violations with recommended solutions
- ⚡ **Performance Solution Flagging** - Identify when Performance Solutions may be required
- 🔄 **Complete Audit Trail** - Full execution trace for documentation purposes
- 🚀 **RESTful API with FastAPI** - Integration-ready architecture

## Intended Users

- **Architects** - Design compliance verification
- **Structural Engineers** - Code requirement validation  
- **Building Certifiers** - Assessment documentation
- **Builders** - Construction compliance checking
- **Building Surveyors** - Regulatory compliance review

## Core Capabilities

### 1. Code Interpretation
Retrieves and interprets relevant NCC/BCA clauses, Deemed-to-Satisfy provisions, and acceptable construction practice guidelines.

### 2. DTS Compliance Assessment
Systematically checks design elements against applicable DTS requirements for:
- Building classification
- Fire safety (Part C, D, E)
- Access and egress (Part D)
- Health and amenity (Part F)
- Energy efficiency (Part J)
- Structural provisions (Part B)
- And all other NCC volumes and sections

### 3. Evidence Documentation
Gathers and organizes:
- Design drawings and specifications
- Material certifications
- Test reports and certificates
- Product technical data
- Calculation sheets

### 4. Compliance Reporting
Generates structured reports including:
- Project summary and classification
- Applicable NCC clauses
- Clause-by-clause compliance assessment
- Evidence references
- Non-compliance findings
- Recommended remediation strategies
- Performance Solution flags where DTS cannot be satisfied

## Project Structure

```
building-consultant-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                           # FastAPI app
│   ├── config.py                         # Configuration settings
│   ├── streamlit_app.py                  # Web UI for compliance checks
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── core.py                       # Agent initialization
│   │   └── tools.py                      # NCC/BCA retrieval tools
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py                    # Pydantic models for compliance
│   └── prompts/
│       ├── __init__.py
│       ├── compliance_agent_prompt.py    # Main compliance orchestrator
│       ├── dts_assessment_prompt.py      # DTS assessment sub-agent
│       └── evidence_gathering_prompt.py  # Evidence collection sub-agent
├── .env                                  # Environment variables
├── .gitignore
├── requirements.txt
├── start.sh                              # Startup script
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit the `.env` file with your API keys:

```env
APIFY_API_URL=your_apify_api_url_here
OPENAI_API_KEY=your_openai_key_here
MODEL_NAME=gpt-4o-mini
```

**Note:** The agent uses web search capabilities to retrieve up-to-date NCC/BCA information from official sources like ABCB.gov.au and accredited reference materials.

### 3. Run the API

```bash
./start.sh
```

Or manually:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the Web UI (Optional)

```bash
streamlit run app/streamlit_app.py
```

## API Endpoints

### GET /
Health check endpoint.

**Response:**
```json
{
  "message": "Building Consultant Agent API is running"
}
```

### POST /assess-compliance
Assess a building design for NCC/BCA DTS compliance.

**Request:**
```json
{
  "project_description": "3-storey residential apartment building, Class 2, Victoria",
  "building_class": "Class 2",
  "assessment_scope": "Fire safety egress and accessibility compliance",
  "design_details": "Refer to uploaded drawings DA-01 to DA-15",
  "specific_concerns": "Stairway width and fire-rated construction"
}
```

**Response:**
```json
{
  "success": true,
  "final_response": "Compliance assessment complete. See detailed report.",
  "execution_trace": [...],
  "files": {
    "compliance_report.md": "# NCC/BCA Compliance Assessment Report\n\n...",
    "non_compliance_summary.md": "# Non-Compliance Items\n\n...",
    "evidence_checklist.md": "# Required Evidence Documentation\n\n..."
  },
  "compliance_summary": {
    "compliant_clauses": 34,
    "non_compliant_clauses": 3,
    "performance_solution_required": 1,
    "overall_status": "Non-Compliant - Remediation Required"
  }
}
```

### GET /health
Health check with agent status.

**Response:**
```json
{
  "status": "healthy",
  "agent": "initialized"
}
```

## Usage Examples

### Example 1: Fire Safety Compliance Check

```python
import requests

response = requests.post(
    "http://localhost:8000/assess-compliance",
    json={
        "project_description": "Type A construction, 4-storey office building",
        "building_class": "Class 5",
        "assessment_scope": "Fire resistance and egress compliance - NCC Volume 1",
        "design_details": "FRL requirements for structural elements and fire doors",
        "specific_concerns": "Fire-rated walls between tenancies and exit door specifications"
    }
)

print(response.json()["files"]["compliance_report.md"])
```

### Example 2: Accessibility Assessment

```python
response = requests.post(
    "http://localhost:8000/assess-compliance",
    json={
        "project_description": "Single storey medical centre with public access",
        "building_class": "Class 6",
        "assessment_scope": "Access and mobility requirements - Part D3",
        "design_details": "Main entrance, accessible parking, sanitary facilities layout",
        "specific_concerns": "Compliant accessible toilet and ramp gradients"
    }
)
```

## Agent Architecture

### Main Agent: Building Compliance Orchestrator
- Coordinates the overall compliance assessment workflow
- Determines applicable NCC/BCA volumes and sections
- Delegates specialized tasks to sub-agents
- Synthesizes findings into comprehensive reports
- Flags non-compliances and recommends solutions

### Sub-Agent 1: DTS Assessment Specialist
- Retrieves specific NCC/BCA clauses and DTS provisions
- Performs detailed clause-by-clause analysis
- Compares design specifications against code requirements
- Identifies compliant and non-compliant elements
- Recommends remediation strategies for non-compliances

### Sub-Agent 2: Evidence Gathering Specialist
- Identifies required supporting documentation
- Extracts design parameters from project descriptions
- Creates evidence checklists
- Verifies documentation completeness
- Maps evidence to specific code clauses

## Workflow

1. **Project Intake** - Receive project description, classification, and scope
2. **Code Identification** - Determine applicable NCC/BCA clauses
3. **DTS Retrieval** - Fetch relevant Deemed-to-Satisfy provisions
4. **Evidence Collection** - Gather design specifications and documentation
5. **Compliance Assessment** - Compare design against each applicable clause
6. **Gap Analysis** - Identify non-compliances and missing evidence
7. **Solution Recommendation** - Propose compliant alternatives or flag Performance Solutions
8. **Report Generation** - Produce clause-by-clause assessment and executive summary

## Output Files

### 1. compliance_report.md
Comprehensive clause-by-clause assessment with:
- Project classification and applicable codes
- DTS provisions checked
- Compliance status for each clause
- Evidence references
- Overall compliance determination

### 2. non_compliance_summary.md
Focused summary of code violations:
- Clause reference
- Requirement description
- Current design non-compliance
- Recommended compliant solution
- Performance Solution flag (if applicable)

### 3. evidence_checklist.md
Documentation requirements:
- Required certificates and test reports
- Missing documentation items
- Additional information needed
- Suggested next steps

## Limitations

### What This Agent DOES:
- ✅ Interpret NCC/BCA clauses and DTS requirements
- ✅ Assess design compliance against DTS provisions
- ✅ Identify non-compliances and suggest solutions
- ✅ Flag when Performance Solutions may be needed
- ✅ Generate detailed compliance documentation

### What This Agent DOES NOT Do:
- ❌ Provide legal or regulatory advice (consult certified professionals)
- ❌ Replace qualified building certifiers or surveyors
- ❌ Perform structural calculations or engineering analysis
- ❌ Write Performance Solutions (unless explicitly requested)
- ❌ Guarantee regulatory approval

**Disclaimer:** This tool provides guidance based on publicly available NCC/BCA information. All compliance assessments must be verified by qualified and registered building professionals. Always consult licensed certifiers, engineers, and architects for final approval.

## Future Enhancements

- Integration with CAD/BIM systems for automatic dimension extraction
- Direct ABCB database integration for real-time code updates
- State-specific variation detection (QLD, NSW, VIC, etc.)
- Performance Solution development assistance
- Multi-project portfolio tracking

## Support

For issues, questions, or feature requests, please contact the development team or refer to the project documentation.

## License

[Specify your license here]

---

**Built with:** FastAPI, DeepAgents, LangChain, OpenAI GPT-4
