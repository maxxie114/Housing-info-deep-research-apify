# Building Consultant Deep Agent

> **⚠️ IMPORTANT: This agent has been transformed from a competitive research agent to a Building Compliance Consultant specializing in Australian NCC/BCA Deemed-to-Satisfy (DTS) assessment.**

AI-powered building code compliance assistant specializing in Australian NCC/BCA Deemed-to-Satisfy (DTS) assessment, clause interpretation, and compliance reporting.

## 🏗️ Overview

This intelligent agent assists building professionals by automating the tedious process of NCC/BCA code compliance checking. It retrieves relevant clauses, assesses designs against Deemed-to-Satisfy provisions, gathers evidence, and generates comprehensive compliance reports.

## ✨ Features

- 🏗️ **NCC/BCA Code Retrieval** - Access and interpret Australian building code clauses
- ✅ **DTS Compliance Assessment** - Automated Deemed-to-Satisfy requirement checking  
- 📋 **Evidence Gathering** - Systematic collection of design documentation and specifications
- 📊 **Clause-by-Clause Analysis** - Detailed comparison of design against code requirements
- 📝 **Compliance Report Generation** - Professional reports for architects, engineers, certifiers, and builders
- 🚨 **Non-Compliance Detection** - Identification of code violations with recommended solutions
- ⚡ **Performance Solution Flagging** - Identify when Performance Solutions may be required
- 🔄 **Complete Audit Trail** - Full execution trace for documentation purposes
- 🚀 **RESTful API with FastAPI** - Integration-ready architecture

## 👥 Intended Users

- **Architects** - Design compliance verification
- **Structural Engineers** - Code requirement validation  
- **Building Certifiers** - Assessment documentation
- **Builders** - Construction compliance checking
- **Building Surveyors** - Regulatory compliance review

## 📁 Project Structure

```
building-consultant-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                           # FastAPI app with compliance endpoints
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

## 🚀 Setup

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

## 📡 API Endpoints

### GET /
Health check endpoint showing agent capabilities.

**Response:**
```json
{
  "message": "Building Consultant Agent API is running",
  "specialization": "Australian NCC/BCA DTS Compliance Assessment",
  "capabilities": [
    "Code clause retrieval",
    "DTS compliance assessment",
    "Evidence gathering",
    "Compliance report generation",
    "Non-compliance identification",
    "Performance Solution flagging"
  ]
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
  "design_details": "Fire-rated walls 90/90/90, exit stairways 1000mm width, accessible toilets on ground floor",
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

### POST /research (Legacy)
Legacy research endpoint maintained for backward compatibility.

### GET /health
Health check with agent status.

**Response:**
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "agent_type": "Building Compliance Consultant",
  "specialization": "NCC/BCA DTS Assessment"
}
```

## 💡 Usage Examples

### Example 1: Fire Safety Compliance Check

```python
import requests

response = requests.post(
    "http://localhost:8000/assess-compliance",
    json={
        "project_description": "Type A construction, 4-storey office building, Class 5, Sydney NSW",
        "building_class": "Class 5",
        "assessment_scope": "Fire resistance and egress compliance - NCC Volume 1",
        "design_details": "FRL requirements for structural elements and fire doors. Exit stairways 1200mm width.",
        "specific_concerns": "Fire-rated walls between tenancies and exit door specifications"
    }
)

result = response.json()
print(result["files"]["compliance_report.md"])
```

### Example 2: Accessibility Assessment

```python
response = requests.post(
    "http://localhost:8000/assess-compliance",
    json={
        "project_description": "Single storey medical centre with public access, Class 6, Melbourne VIC",
        "building_class": "Class 6",
        "assessment_scope": "Access and mobility requirements - Part D3",
        "design_details": "Main entrance via ramp 1:14 gradient, accessible parking 2 spaces, accessible toilet on ground floor",
        "specific_concerns": "Compliant accessible toilet dimensions and ramp handrails"
    }
)
```

### Example 3: Using the Web UI

1. Start the backend: `./start.sh`
2. Start Streamlit: `streamlit run app/streamlit_app.py`
3. Open browser to `http://localhost:8501`
4. Fill in project details:
   - **Building Class**: Class 2
   - **Assessment Scope**: Fire safety and accessibility
   - **Project Description**: Full project details
5. Click "Assess Compliance"
6. Review generated compliance reports

## 🏗️ Agent Architecture

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

## 📋 Assessment Workflow

1. **Project Intake** - Receive project description, classification, and scope
2. **Code Identification** - Determine applicable NCC/BCA clauses
3. **DTS Retrieval** - Fetch relevant Deemed-to-Satisfy provisions
4. **Evidence Collection** - Gather design specifications and documentation
5. **Compliance Assessment** - Compare design against each applicable clause
6. **Gap Analysis** - Identify non-compliances and missing evidence
7. **Solution Recommendation** - Propose compliant alternatives or flag Performance Solutions
8. **Report Generation** - Produce clause-by-clause assessment and executive summary

## 📄 Output Files

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

## ⚠️ Limitations & Disclaimers

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

## 🔧 Development

### Running Tests (if implemented)

```bash
pytest
```

### Linting

```bash
ruff check .
```

## 📚 Additional Resources

- [Australian Building Codes Board (ABCB)](https://www.abcb.gov.au/)
- [NCC Online](https://ncc.abcb.gov.au/)
- [Building Professionals Board (VIC)](https://www.vba.vic.gov.au/)
- [Fair Trading NSW - Building Professionals](https://www.fairtrading.nsw.gov.au/housing-and-property/building-and-renovating)

## 📝 Migration Notes

This agent was previously a competitive research agent. The transformation included:
- Complete prompt redesign for building code compliance
- New sub-agents for DTS assessment and evidence gathering
- Updated schemas for compliance requests/responses
- Modified tools for NCC/BCA code retrieval
- New Streamlit UI for compliance assessments
- Enhanced API with dedicated compliance endpoint

Legacy research functionality is maintained via the `/research` endpoint for backward compatibility.

## 📄 License

[Specify your license here]

---

**Built with:** FastAPI, DeepAgents, LangChain, OpenAI GPT-4

**Specialization:** Australian NCC/BCA Deemed-to-Satisfy Compliance Assessment

async def research(topic: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/research",
            json={"topic": topic}
        )
        return response.json()

result = asyncio.run(research("AI agents in 2025"))
print(result)
```

## Agent Capabilities

The research agent can:

1. **Create Task Lists**: Break down research into manageable tasks
2. **Web Search**: Gather current information from the internet
3. **File Writing**: Save findings and reports
4. **Delegate to Sub-agents**: Use specialized data analyzer for detailed reports
5. **Track Progress**: Monitor research tasks

## Configuration

Modify `app/config.py` to customize settings:

```python
class Settings(BaseSettings):
    tavily_api_key: str
    openai_api_key: str
    model_name: str = "gpt-4o-mini"
```

## Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload --log-level debug
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Requirements

- Python 3.8+
- OpenAI API key
- Tavily API key

## License

MIT
