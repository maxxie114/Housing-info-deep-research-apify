from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from app.agent.core import initialize_agent, get_agent
from app.models.schemas import (
    ResearchRequest, ResearchResponse,
    ComplianceRequest, ComplianceResponse, ComplianceSummary
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize agent at startup"""
    logger.info("Initializing building compliance agent...")
    try:
        initialize_agent()
        logger.info("Building compliance agent ready")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise
    finally:
        logger.info("Shutting down")

app = FastAPI(
    title="Building Consultant Agent API",
    description="AI-powered NCC/BCA compliance assessment with Deemed-to-Satisfy analysis and reporting",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
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

@app.post("/assess-compliance", response_model=ComplianceResponse)
async def assess_compliance(request: ComplianceRequest):
    """
    Assess building design for NCC/BCA Deemed-to-Satisfy compliance
    
    This endpoint performs comprehensive code compliance assessment including:
    - Applicable code clause identification
    - DTS requirement retrieval
    - Design specification extraction
    - Clause-by-clause compliance analysis
    - Non-compliance identification with solutions
    - Evidence documentation requirements
    - Performance Solution flagging where needed
    """
    try:
        agent = get_agent()
        
        # Construct comprehensive compliance assessment prompt
        assessment_prompt = f"""Assess the following building project for NCC/BCA Deemed-to-Satisfy compliance:

**Project Description:** {request.project_description}

**Building Classification:** {request.building_class}

**Assessment Scope:** {request.assessment_scope}

**Design Details:** {request.design_details or "To be extracted from project description"}

**Specific Concerns:** {request.specific_concerns or "General comprehensive compliance assessment"}

Please conduct a thorough DTS compliance assessment following your systematic workflow:
1. Determine applicable NCC volumes, parts, and clauses
2. Retrieve specific DTS requirements for all applicable areas
3. Extract design specifications and identify evidence requirements
4. Perform clause-by-clause compliance analysis
5. Generate comprehensive compliance report, non-compliance summary, and evidence checklist

Provide your final assessment summary clearly noting overall compliance status, critical issues, and recommended actions."""
        
        # Invoke agent
        result = agent.invoke({
            "messages": [{"role": "user", "content": assessment_prompt}]
        })
        
        # Process execution trace
        trace = []
        files = {}
        
        for i, msg in enumerate(result.get("messages", [])):
            if hasattr(msg, 'type'):
                trace_item = {
                    "message_index": i,
                    "type": msg.type
                }
                
                if msg.type == "ai":
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        trace_item["tool_calls"] = [
                            {"name": tc.get('name'), "args": tc.get('args', {})}
                            for tc in msg.tool_calls
                        ]
                    trace_item["content_preview"] = msg.content[:200] if msg.content else None
                    
                elif msg.type == "tool":
                    trace_item["tool_name"] = getattr(msg, 'name', '')
                    trace_item["content_preview"] = str(msg.content)[:200] if msg.content else None
                    
                elif msg.type == "human":
                    trace_item["content_preview"] = msg.content[:200] if msg.content else None
                
                trace.append(trace_item)
        
        # Extract files if present and convert to strings
        if "files" in result and result["files"]:
            for file_path, file_data in result["files"].items():
                if isinstance(file_data, dict) and "content" in file_data:
                    content = file_data["content"]
                    if isinstance(content, list):
                        files[file_path] = "\n".join(content)
                    else:
                        files[file_path] = str(content)
                else:
                    files[file_path] = str(file_data)
        
        # Get final response
        final_message = result["messages"][-1] if result.get("messages") else None
        final_response = final_message.content if final_message else "No response generated"
        
        # Parse compliance summary from final response (simple heuristic)
        compliance_summary = ComplianceSummary()
        if final_response:
            # Try to extract compliance statistics from response
            response_lower = final_response.lower()
            if "compliant" in response_lower and "non-compliant" not in response_lower:
                compliance_summary.overall_status = "Compliant"
            elif "non-compliant" in response_lower:
                compliance_summary.overall_status = "Non-Compliant - Remediation Required"
            elif "performance solution" in response_lower:
                compliance_summary.overall_status = "Performance Solution Required"
                compliance_summary.performance_solution_required = 1
        
        return ComplianceResponse(
            success=True,
            final_response=final_response,
            execution_trace=trace,
            files=files,
            compliance_summary=compliance_summary
        )
        
    except Exception as e:
        logger.error(f"Compliance assessment error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Legacy research endpoint (maintained for backward compatibility)
@app.post("/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    """Execute research on a given topic (legacy endpoint)"""
    try:
        agent = get_agent()
        
        # Invoke agent
        result = agent.invoke({
            "messages": [{"role": "user", "content": request.topic}]
        })
        
        # Process execution trace
        trace = []
        files = {}
        
        for i, msg in enumerate(result.get("messages", [])):
            if hasattr(msg, 'type'):
                trace_item = {
                    "message_index": i,
                    "type": msg.type
                }
                
                if msg.type == "ai":
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        trace_item["tool_calls"] = [
                            {"name": tc.get('name'), "args": tc.get('args', {})}
                            for tc in msg.tool_calls
                        ]
                    trace_item["content_preview"] = msg.content[:200] if msg.content else None
                    
                elif msg.type == "tool":
                    trace_item["tool_name"] = getattr(msg, 'name', '')
                    trace_item["content_preview"] = str(msg.content)[:200] if msg.content else None
                    
                elif msg.type == "human":
                    trace_item["content_preview"] = msg.content[:200] if msg.content else None
                
                trace.append(trace_item)
        
        # Extract files if present and convert to strings
        if "files" in result and result["files"]:
            for file_path, file_data in result["files"].items():
                if isinstance(file_data, dict) and "content" in file_data:
                    # Extract content from dict, join if it's a list
                    content = file_data["content"]
                    if isinstance(content, list):
                        files[file_path] = "\n".join(content)
                    else:
                        files[file_path] = str(content)
                else:
                    files[file_path] = str(file_data)
        
        # Get final response
        final_message = result["messages"][-1] if result.get("messages") else None
        final_response = final_message.content if final_message else "No response generated"
        
        return ResearchResponse(
            success=True,
            final_response=final_response,
            execution_trace=trace,
            files=files
        )
        
    except Exception as e:
        logger.error(f"Research error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        agent = get_agent()
        return {
            "status": "healthy",
            "agent_initialized": agent is not None,
            "agent_type": "Building Compliance Consultant",
            "specialization": "NCC/BCA DTS Assessment"
        }
    except:
        return {
            "status": "unhealthy",
            "agent_initialized": False
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
