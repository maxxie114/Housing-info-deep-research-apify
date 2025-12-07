# File Upload Feature Guide

## Overview

The Building Consultant Deep Agent now supports **automatic document processing** via file uploads. Instead of manually copying and pasting building specifications, you can upload PDF, DOCX, or TXT files directly.

## Supported File Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| PDF | `.pdf` | Building plans, compliance reports, specifications |
| Word Documents | `.docx` | Architectural specifications, assessment reports |
| Text Files | `.txt` | Plain text documentation, notes |

## How It Works

### 1. Text Extraction
When you upload a file, the system automatically:
- Extracts all text content from the document
- Preserves document structure and formatting where possible
- Displays a preview of the extracted content
- Allows you to upload multiple files simultaneously

### 2. Auto-fill Mechanism
- Extracted text is combined from all uploaded files
- Each file's content is labeled with its filename
- Text is automatically populated into the project description field
- You can still edit or add additional context manually

### 3. Processing
- Extracted text is combined with any manually entered information
- The complete content is sent to the compliance assessment agent
- The agent analyzes the combined information for NCC/BCA compliance

## Usage Examples

### Example 1: Web UI (Streamlit)

1. **Navigate to the application**: `http://localhost:8501`

2. **Upload Files** (in the sidebar):
   - Click "Browse files" under "📁 Upload Building Documentation"
   - Select one or more files (e.g., `building_spec.pdf`, `drawings.docx`)
   - View the extracted text preview

3. **Auto-fill**:
   - Click "📋 Auto-fill from Uploaded Files"
   - Review the populated text in the "Project Description" field

4. **Configure Assessment**:
   - Select Building Class (e.g., "Class 2")
   - Enter Assessment Scope (e.g., "Fire safety and accessibility")

5. **Run Assessment**:
   - Click "🔍 Assess Compliance"
   - Wait for the comprehensive compliance report

### Example 2: API Endpoint

**Upload files with multipart form data:**

```bash
curl -X POST http://localhost:8000/assess-compliance-with-files \
  -F "building_class=Class 2" \
  -F "assessment_scope=Fire safety and accessibility" \
  -F "project_description=3-storey apartment building" \
  -F "files=@/path/to/building_specification.pdf" \
  -F "files=@/path/to/architectural_drawings.docx" \
  -F "specific_concerns=Stairway dimensions, fire door ratings"
```

**Response:**
```json
{
  "success": true,
  "final_response": "Executive Summary...",
  "compliance_summary": {
    "compliant_clauses": 12,
    "non_compliant_clauses": 3,
    "performance_solution_required": 1,
    "overall_status": "Partially Compliant"
  },
  "files": {
    "compliance_report.md": "...",
    "non_compliance_summary.md": "...",
    "evidence_checklist.md": "..."
  },
  "execution_trace": [...]
}
```

### Example 3: Python Script

```python
import requests

# Prepare files
files = [
    ('files', ('building_spec.pdf', open('building_spec.pdf', 'rb'), 'application/pdf')),
    ('files', ('drawings.docx', open('drawings.docx', 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
]

# Prepare form data
data = {
    'building_class': 'Class 2',
    'assessment_scope': 'Fire safety and accessibility',
    'project_description': 'Additional context if needed',
    'specific_concerns': 'Stairway dimensions'
}

# Send request
response = requests.post(
    'http://localhost:8000/assess-compliance-with-files',
    files=files,
    data=data
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Compliance Status: {result['compliance_summary']['overall_status']}")
```

## Tips for Best Results

### 1. **File Quality**
- Use clear, well-formatted documents
- Ensure PDF text is selectable (not scanned images)
- Use properly structured Word documents with headings

### 2. **Multiple Files**
- Upload all relevant documents together
- Each file's content will be clearly labeled
- Combine specifications, plans, and reports for comprehensive assessment

### 3. **Hybrid Approach**
- Upload files for bulk content
- Add specific details manually in the text fields
- Highlight particular concerns in the "Specific Concerns" field

### 4. **Document Organization**
Recommended files to upload:
- Building specifications (PDF/DOCX)
- Architectural drawings reference list (TXT)
- Previous compliance reports (PDF)
- Design rationale documents (DOCX)
- Fire safety strategy (PDF)

## Technical Details

### Backend Implementation

**Extraction Functions:**
```python
# PDF Extraction (using PyPDF2)
from PyPDF2 import PdfReader
pdf_reader = PdfReader(file_content)
text = "".join([page.extract_text() for page in pdf_reader.pages])

# DOCX Extraction (using python-docx)
from docx import Document
doc = Document(file_content)
text = "\n".join([para.text for para in doc.paragraphs])

# TXT Extraction
text = file_content.decode('utf-8')
```

**API Endpoint:**
- Route: `/assess-compliance-with-files`
- Method: `POST`
- Content-Type: `multipart/form-data`
- Parameters:
  - `building_class` (required): NCC building classification
  - `assessment_scope` (required): Focus areas for assessment
  - `project_description` (optional): Additional manual description
  - `design_details` (optional): Specific design information
  - `specific_concerns` (optional): Particular compliance questions
  - `files` (optional): List of uploaded files

### Dependencies

```txt
pypdf2==3.0.1
python-docx==1.1.0
python-multipart>=0.0.9
```

## Troubleshooting

### Issue: "Unsupported file type"
**Solution:** Ensure files have `.pdf`, `.docx`, or `.txt` extensions

### Issue: "No text extracted from PDF"
**Solution:** PDF may be scanned image - use OCR tool first or manually enter text

### Issue: "File too large"
**Solution:** Split large files or compress PDFs before uploading

### Issue: "API timeout"
**Solution:** 
- Reduce file size
- Upload fewer files simultaneously
- Increase timeout setting in API call

## Future Enhancements

Potential future improvements:
- [ ] OCR support for scanned PDFs
- [ ] CAD drawing text extraction (.dwg, .dxf)
- [ ] Excel spreadsheet support (.xlsx)
- [ ] Image analysis for building plans
- [ ] Batch processing of multiple projects
- [ ] Direct integration with document management systems

## Support

For issues or questions about file upload functionality:
1. Check this guide for common solutions
2. Verify file format compatibility
3. Test with the provided sample files
4. Review backend logs for extraction errors

---

**Last Updated:** December 2024  
**Version:** 2.0 (File Upload Feature)
