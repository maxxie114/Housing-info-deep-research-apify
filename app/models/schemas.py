from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class ComplianceRequest(BaseModel):
    project_description: str = Field(..., min_length=10, description="Project description including building type, size, location")
    building_class: str = Field(..., description="NCC Building Classification (e.g., Class 1a, Class 2, Class 5)")
    assessment_scope: str = Field(..., description="Scope of compliance assessment (e.g., Fire safety, Accessibility, Energy efficiency)")
    design_details: Optional[str] = Field(None, description="Specific design details, drawings, or specifications")
    specific_concerns: Optional[str] = Field(None, description="Specific compliance concerns or questions")

class ToolCallInfo(BaseModel):
    name: str
    args: Dict[str, Any]

class ExecutionTrace(BaseModel):
    message_index: int
    type: str
    content_preview: Optional[str] = None
    tool_calls: Optional[List[ToolCallInfo]] = None
    tool_name: Optional[str] = None

class ComplianceSummary(BaseModel):
    compliant_clauses: int = 0
    non_compliant_clauses: int = 0
    performance_solution_required: int = 0
    overall_status: str = "Assessment Incomplete"

class ComplianceResponse(BaseModel):
    success: bool
    final_response: str
    execution_trace: List[ExecutionTrace]
    files: Dict[str, str] = {}
    compliance_summary: Optional[ComplianceSummary] = None
    error: Optional[str] = None

# Legacy support - keeping old schemas for backward compatibility
class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=5, description="Research topic/query")

class ResearchResponse(BaseModel):
    success: bool
    final_response: str
    execution_trace: List[ExecutionTrace]
    files: Dict[str, str] = {}
    error: Optional[str] = None
