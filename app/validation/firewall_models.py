from ipaddress import IPv4Address

from pydantic import BaseModel, Field


class PostFirewallModel(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    ip_address: IPv4Address
    port: int = Field(ge=0, le=65_535)
