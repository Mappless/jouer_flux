from __future__ import annotations

import enum
from ipaddress import IPv4Address
from os import name
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import custom_types
from ..base import Base

if TYPE_CHECKING:
    from .filtering_policy import FilteringPolicy


class RuleAction(enum.Enum):
    DENY = "DENY"
    ALLOW = "ALLOW"


class Protocol(enum.Enum):
    ANY = "ANY"
    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"


class Rule(Base):
    __tablename__ = "rule"
    __table_args__ = (
        UniqueConstraint(
            "filtering_policy_id",
            "source_ip",
            "destination_ip",
            "destination_port",
            "protocol",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(50))
    filtering_policy_id: Mapped[int] = mapped_column(ForeignKey("filtering_policy.id"))
    filtering_policy: Mapped[FilteringPolicy] = relationship(
        back_populates="_rules", lazy="joined"
    )
    source_ip: Mapped[IPv4Address] = mapped_column(custom_types.IPv4Address)
    destination_ip: Mapped[IPv4Address] = mapped_column(custom_types.IPv4Address)
    destination_port: Mapped[int]
    protocol: Mapped[Protocol] = mapped_column(Enum(Protocol))
    action: Mapped[RuleAction] = mapped_column(Enum(RuleAction))
    next_rule_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rule.id"))

    def is_similar(self, other: Rule) -> bool:
        return (
            self.filtering_policy_id,
            self.source_ip,
            self.destination_ip,
            self.destination_port,
            self.action,
        ) == (
            other.filtering_policy_id,
            other.source_ip,
            other.destination_ip,
            other.destination_port,
            other.action,
        )

    def __eq__(self, value: object) -> bool:
        if value is None:
            return False
        if not isinstance(value, Rule):
            return False
        return (
            self.filtering_policy_id,
            self.name,
            self.source_ip,
            self.destination_ip,
            self.destination_port,
            self.protocol,
            self.action,
        ) == (
            value.filtering_policy_id,
            value.name,
            value.source_ip,
            value.destination_ip,
            value.destination_port,
            value.protocol,
            value.action,
        )

    def convert_to_json(self, show_filtering_policy: bool = False) -> dict:
        """
        Convert the object into a jsonifiable dict.

        :param show_filtering_policy: Add the firewall in the json

        :return: A jsonifiable dict
        """
        result = {
            "id": self.id,
            "source_ip": str(self.source_ip),
            "destination_ip": str(self.destination_ip),
            "destination_port": self.destination_port,
            "protocol": self.protocol.name,
            "action": self.action.name,
        }

        if name is not None:
            result["name"] = self.name

        if show_filtering_policy:
            result["filtering_policy"] = self.filtering_policy.convert_to_json()

        return result
