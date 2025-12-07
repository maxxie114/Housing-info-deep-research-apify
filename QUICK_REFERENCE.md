# Quick Reference - File Upload Feature

## 🚀 Start the Application

```bash
# Terminal 1: Backend API
cd /Users/pramodthebe/Desktop/deep_research_agent
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2: Web UI
streamlit run app/streamlit_app.py
```

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Web UI | http://localhost:8501 | Streamlit compliance checker |
| API Docs | http://127.0.0.1:8000/docs | Swagger UI documentation |
| Health Check | http://127.0.0.1:8000/health | Backend status |

## 📁 Upload a File

### Via Web UI
1. Open http://localhost:8501
2. Sidebar → "📁 Upload Building Documentation"
3. Click "Browse files" and select .pdf, .docx, or .txt
4. View extracted text preview
5. Click "📋 Auto-fill from Uploaded Files"
6. Select Building Class & Assessment Scope
7. Click "🔍 Assess Compliance"

### Via cURL
```bash
curl -X POST http://localhost:8000/assess-compliance-with-files \
  -F "building_class=Class 2" \
  -F "assessment_scope=Fire safety and accessibility" \
  -F "files=@/path/to/file.pdf"
```

### Via Python
```python
import requests

files = [('files', ('spec.pdf', open('spec.pdf', 'rb'), 'application/pdf'))]
data = {
    'building_class': 'Class 2',
    'assessment_scope': 'Fire safety',
    'project_description': 'Optional additional context'
}

response = requests.post(
    'http://localhost:8000/assess-compliance-with-files',
    files=files,
    data=data
)

print(response.json())
```

## 📋 API Endpoint

**POST `/assess-compliance-with-files`**

**Form Parameters:**
```
building_class      (required)  - NCC class (Class 1a, 1b, 2, 3, 5, 6, 7, 8, 9, 10)
assessment_scope    (required)  - Assessment focus (e.g., "Fire safety")
project_description (optional)  - Manual description text
design_details      (optional)  - Design specifications
specific_concerns   (optional)  - Compliance questions
files               (optional)  - PDF/DOCX/TXT files (multipart)
```

**Response:**
```json
{
  "success": true,
  "final_response": "Executive summary...",
  "compliance_summary": {
    "compliant_clauses": 12,
    "non_compliant_clauses": 2,
    "overall_status": "Mostly Compliant"
  },
  "files": {
    "compliance_report.md": "...",
    "non_compliance_summary.md": "...",
    "evidence_checklist.md": "..."
  }
}
```

## 📄 Supported File Types

| Type | Extension | Notes |
|------|-----------|-------|
| PDF | .pdf | Building plans, reports |
| Word | .docx | Specifications, assessments |
| Text | .txt | Notes, plain text docs |

## 🧪 Test with Sample File

```bash
# Sample test file included in repo
curl -X POST http://localhost:8000/assess-compliance-with-files \
  -F "building_class=Class 2" \
  -F "assessment_scope=Fire safety" \
  -F "files=@test_sample.txt"
```

## 📚 Documentation

- **README.md** - Main documentation
- **FILE_UPLOAD_GUIDE.md** - Detailed user guide
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **DEPLOYMENT_STATUS.md** - Deployment verification
- **QUICKSTART.md** - Getting started guide

## 🔍 Check Backend Status

```bash
curl http://127.0.0.1:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "agent_type": "Building Compliance Consultant"
}
```

## ⚙️ Installed Dependencies

- fastapi==0.115.0
- uvicorn[standard]==0.32.0
- deepagents==0.1.0
- streamlit==1.39.0
- pypdf2==3.0.1 ✨ (new)
- python-docx==1.1.0 ✨ (new)
- python-multipart>=0.0.9 ✨ (new)

## 🔗 GitHub

**Repository:** https://github.com/maxxie114/Housing-info-deep-research-apify  
**Branch:** `bca_agent`  
**Last Commit:** File upload feature implementation

## ❓ Common Issues

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -ti:8000 \| xargs kill -9` |
| Module not found | `pip install -r requirements.txt` |
| File not extracted | Check file format is supported (.pdf/.docx/.txt) |
| API timeout | Large assessment - wait or reduce file size |
| Streamlit not found | `pip install streamlit==1.39.0` |

## 📞 Verify Everything Works

```bash
# 1. Check backend running
curl http://127.0.0.1:8000/health

# 2. Test file upload endpoint
curl -X POST http://localhost:8000/assess-compliance-with-files \
  -F "building_class=Class 2" \
  -F "assessment_scope=Fire safety" \
  -F "files=@test_sample.txt"

# 3. Check API docs
open http://127.0.0.1:8000/docs

# 4. Access Streamlit UI
open http://localhost:8501
```

---

**Version:** 2.0 (File Upload Feature)  
**Date:** December 6, 2025  
**Status:** ✅ Production Ready
