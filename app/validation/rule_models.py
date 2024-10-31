from ipaddress import IPv4Address
from typing import Optional

from pydantic import BaseModel, Field

from app.db.models import Protocol, RuleAction


class PostRuleModel(BaseModel):
    previous_rule_id: Optional[int] = None
    name: Optional[str] = Field(min_length=0, max_length=50, default=None)
    source_ip: IPv4Address
    destination_ip: IPv4Address
    destination_port: int = Field(ge=0, le=65535)
    protocol: Protocol
    action: RuleAction
