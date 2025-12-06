from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class InstagramPost(BaseModel):
    """
    Represents a single Instagram post.
    """

    url: str = Field(description='The URL of the post.')
    likes: int = Field(description='The number of likes.')
    comments: int = Field(description='The number of comments.')
    timestamp: str = Field(description='The timestamp of the post.')
    caption: str | None = Field(description='The caption of the post.')
    alt: str | None = Field(description='The alt text of the post.')

class AgentStructuredOutput(BaseModel):
    """
    The structured output from the agent.
    """

    answer: str = Field(description='The answer to the user query.')
    instagram_posts: list[InstagramPost] = Field(
        description='A list of Instagram posts scraped from the profile.', default_factory=list
    )


class BCARequirement(BaseModel):
    category: str                     # e.g. "Stairs", "Balustrades", "Fire separation"
    code_reference: Optional[str]     # e.g. "NCC 2022 Vol 2 Part 3.9.1, Clause 3.9.1.1"
    requirement: str                  # plain-language requirement
    applicability: Optional[str]      # when/where it applies (Class, storeys, etc.)
    notes: Optional[str] = None       # clarifications, assumptions


class BCARequirementReport(BaseModel):
    task: str
    assumed_location: str             # e.g. "Australia, NCC 2022"
    assumed_volume: Optional[str]     # "Volume One", "Volume Two", etc.
    assumptions: List[str]            # key assumptions the model made
    requirements: List[BCARequirement]
