from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field





class BuildingCodeRequirement(BaseModel):
    category: str                     # e.g. "Stairs", "Parking", "Setbacks"
    code_reference: Optional[str]     # e.g. "CBC 2022 Section 1011.2", "LAMC 12.21"
    requirement: str                  # plain-language requirement
    applicability: Optional[str]      # e.g. "R-2 Occupancy", "Zones R1"
    notes: Optional[str] = None       # clarifications, assumptions


class BuildingCodeReport(BaseModel):
    task: str
    jurisdiction: str                 # e.g. "California", "Los Angeles", "San Francisco"
    code_source: Optional[str]        # e.g. "California Building Code 2022", "Municode"
    assumptions: List[str]            # key assumptions the model made
    requirements: List[BuildingCodeRequirement]
