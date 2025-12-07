# Quick Start Guide - Building Consultant Deep Agent

## 5-Minute Setup

### Prerequisites
- Python 3.10+
- OpenAI API key
- Apify API URL (for web search)

### Step 1: Install Dependencies (1 min)
```bash
cd /Users/pramodthebe/Desktop/deep_research_agent
pip install -r requirements.txt
```

### Step 2: Configure Environment (1 min)
Edit `.env` file:
```env
APIFY_API_URL=your_apify_api_url
OPENAI_API_KEY=your_openai_key
MODEL_NAME=gpt-4o-mini
```

### Step 3: Start the API (30 sec)
```bash
./start.sh
```

Or manually:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Test It Works (30 sec)
Open browser: http://localhost:8000

You should see:
```json
{
  "message": "Building Consultant Agent API is running",
  "specialization": "Australian NCC/BCA DTS Compliance Assessment"
}
```

### Step 5: Run Your First Assessment (2 min)

#### Option A: Web UI (Recommended)
```bash
# In a new terminal
streamlit run app/streamlit_app.py
```

Then:
1. Open http://localhost:8501
2. Select **Building Class**: Class 2
3. Enter **Assessment Scope**: Fire safety compliance
4. Enter **Project Description**:
   ```
   3-storey residential apartment building, Class 2, Melbourne VIC.
   Type A construction, 12 units across 3 levels.
   Total floor area 1,200m². Exit stairways 1000mm width.
   Fire-rated walls 90/90/90.
   ```
5. Click **"Assess Compliance"**
6. Wait 1-2 minutes for comprehensive assessment
7. Review generated compliance reports!

#### Option B: API Call
```python
import requests

response = requests.post(
    "http://localhost:8000/assess-compliance",
    json={
        "project_description": "3-storey Class 2 apartment building, Melbourne VIC",
        "building_class": "Class 2",
        "assessment_scope": "Fire safety and accessibility",
        "design_details": "FRL 90/90/90, exit stairways 1000mm",
        "specific_concerns": "Fire door compliance"
    }
)

result = response.json()
print(result["files"]["compliance_report.md"])
```

## What You Get

After assessment completes, you'll receive:

1. **📋 compliance_report.md**
   - Full clause-by-clause analysis
   - Executive summary
   - Compliance status for each NCC provision
   - Evidence requirements

2. **❌ non_compliance_summary.md**
   - Critical issues requiring attention
   - Recommended compliant solutions
   - Priority action matrix

3. **📄 evidence_checklist.md**
   - Required documentation
   - Missing evidence gaps
   - Certification requirements

## Sample Output Preview

```markdown
# NCC/BCA Compliance Assessment Report

## Executive Summary

**Overall Compliance Status:** NON-COMPLIANT - Remediation Required

**Summary Statistics:**
- Total Clauses Assessed: 28
- Compliant Clauses: 24
- Non-Compliant Clauses: 4
- Performance Solutions Required: 0

**Critical Findings:**
Fire egress provisions comply with Part D1 requirements. 
Accessible toilet dimensions require modification to meet Part D3.8.
Fire door FRL ratings verified compliant with Part C3.11.

[... detailed clause-by-clause analysis follows ...]
```

## Common Use Cases

### 1. Fire Safety Assessment
```python
{
  "project_description": "4-storey office building, Class 5",
  "building_class": "Class 5",
  "assessment_scope": "Fire resistance and egress - Parts C, D, E",
  "design_details": "Type A construction, FRL requirements for walls and floors",
  "specific_concerns": "Exit travel distances and fire door specifications"
}
```

### 2. Accessibility Check
```python
{
  "project_description": "Single storey medical centre, Class 6",
  "building_class": "Class 6",
  "assessment_scope": "Accessibility compliance - Part D3",
  "design_details": "Accessible entrance via ramp, accessible toilet on ground floor",
  "specific_concerns": "Ramp gradient and accessible toilet dimensions"
}
```

### 3. Residential Compliance
```python
{
  "project_description": "Two-storey Class 1a dwelling, timber frame",
  "building_class": "Class 1a",
  "assessment_scope": "Structural, fire safety, and energy efficiency",
  "design_details": "Timber frame with brick veneer, BAL-12.5 zone",
  "specific_concerns": "Bushfire construction requirements"
}
```

## Troubleshooting

### Agent Not Initializing
```bash
# Check logs
tail -f logs/app.log  # if logging to file

# Or check terminal output for errors
```

**Common fixes:**
- Verify OPENAI_API_KEY is set correctly
- Ensure APIFY_API_URL is valid
- Check Python version (requires 3.10+)

### No Search Results
If the agent can't retrieve NCC clauses:
- Verify internet connection
- Check APIFY_API_URL is active
- Try manual search at https://ncc.abcb.gov.au to verify accessibility

### Assessment Takes Too Long
Normal assessment time: 1-3 minutes depending on scope

If stuck:
- Check API logs for errors
- Verify model is responding (check OpenAI API status)
- Try reducing assessment scope to specific NCC parts

## Key Features to Try

### 1. Multiple Building Classes
Test different building types:
- Class 1a (detached houses)
- Class 2 (apartments)
- Class 5 (offices)
- Class 6 (retail)
- Class 9a (health care)

### 2. Specific NCC Parts
Focus on particular code sections:
- Part B: Structure
- Part C: Fire Resistance
- Part D: Access and Egress (D3: Accessibility)
- Part E: Services and Equipment
- Part F: Health and Amenity
- Part J: Energy Efficiency

### 3. State Variations
Mention specific states for state-specific requirements:
- "Melbourne, VIC"
- "Sydney, NSW"
- "Brisbane, QLD"

## Next Steps

1. **Explore the prompts** - See how the agent thinks:
   - `app/prompts/compliance_agent_prompt.py`
   - `app/prompts/dts_assessment_prompt.py`
   - `app/prompts/evidence_gathering_prompt.py`

2. **Customize for your needs** - Modify prompts to:
   - Focus on specific building types
   - Emphasize particular compliance areas
   - Adjust report formats

3. **Integrate into workflows** - Use API endpoints in:
   - Design review processes
   - Pre-certification checks
   - Client reporting systems

4. **Review outputs** - Compare agent assessments with:
   - Manual code checks
   - Certifier feedback
   - Actual approval outcomes

## Getting Help

- **Documentation**: See `README.md` and `README_BUILDING_CONSULTANT.md`
- **Migration Details**: Check `MIGRATION_SUMMARY.md`
- **API Docs**: Visit http://localhost:8000/docs (when running)

## Important Reminders

⚠️ **This agent provides guidance only**
- Not a replacement for registered building certifiers
- Always verify with qualified professionals
- Does not guarantee regulatory approval

✅ **Best used for:**
- Initial compliance screening
- Design review preparation
- Documentation planning
- Code requirement research

---

**Ready to assess building compliance!** 🏗️

For detailed documentation, see the main README files.
