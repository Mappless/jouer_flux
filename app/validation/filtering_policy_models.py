from typing import Optional
from pydantic import BaseModel, Field


class PostFilteringPolicyModel(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    previous_filtering_policy_id: Optional[int] = None
