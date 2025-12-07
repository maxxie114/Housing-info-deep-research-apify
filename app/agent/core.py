from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from app.config import settings
from app.agent.tools import create_search_tool, ncc_bca_search
from app.prompts.compliance_agent_prompt import compliance_agent_prompt
from app.prompts.dts_assessment_prompt import dts_assessment_prompt
from app.prompts.evidence_gathering_prompt import evidence_gathering_prompt

# Global agent instance
building_compliance_agent = None

def initialize_agent():
    """Initialize the building compliance agent once at startup"""
    global building_compliance_agent
    
    # Create NCC/BCA search tool
    search_tool = create_search_tool(settings.apify_api_url)

    # DTS Assessment sub-agent (code retrieval and interpretation specialist)
    dts_assessment_subagent = {
        "name": "dts-assessment-agent",
        "description": "Expert in NCC/BCA code clause retrieval and DTS provision interpretation. Use for retrieving specific code requirements (e.g., 'Get NCC 2022 Part D3 accessible toilet requirements', 'Find BCA fire door FRL requirements for Class 5 buildings', 'Retrieve Part C egress travel distance limits'). Always call with ONE specific code topic. For multiple topics, call multiple times in parallel.",
        "system_prompt": dts_assessment_prompt,
        "tools": [ncc_bca_search],
        "model": settings.model_name,
    }

    # Evidence Gathering sub-agent (specification extraction and documentation specialist)
    evidence_gathering_subagent = {
        "name": "evidence-gathering-agent",
        "description": "Expert in extracting design specifications and creating documentation checklists. Use for identifying what evidence is required for compliance (e.g., 'Extract design specifications from project description', 'Create evidence checklist for fire safety compliance', 'Identify missing documentation for accessibility assessment'). Optionally specify focus areas.",
        "system_prompt": evidence_gathering_prompt,
        "tools": [ncc_bca_search],
        "model": settings.model_name,
    }

    # Initialize model
    model = init_chat_model(settings.model_name)

    # Create building compliance agent with sub-agents
    compliance_agent = create_deep_agent(
        model=model,
        tools=[ncc_bca_search],
        system_prompt=compliance_agent_prompt,
        subagents=[dts_assessment_subagent, evidence_gathering_subagent],
    )

    # Optional recursion limit to allow deep planning
    building_compliance_agent = compliance_agent.with_config({"recursion_limit": 1000})
    
    return building_compliance_agent

def get_agent():
    """Get the initialized agent"""
    if building_compliance_agent is None:
        raise RuntimeError("Building compliance agent not initialized")
    return building_compliance_agent
