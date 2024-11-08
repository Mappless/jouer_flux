from __future__ import annotations

from ipaddress import IPv4Address
from typing import TYPE_CHECKING, List

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import custom_types
from ..base import Base

if TYPE_CHECKING:
    from .filtering_policy import FilteringPolicy


class Firewall(Base):
    __tablename__ = "firewall"
    __table_args__ = (UniqueConstraint("ip_address", "port"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    ip_address: Mapped[IPv4Address] = mapped_column(custom_types.IPv4Address)
    port: Mapped[int] = mapped_column()
    _filtering_policies: Mapped[List[FilteringPolicy]] = relationship(
        back_populates="firewall", cascade="all, delete-orphan"
    )
    _is_filtering_policies_list_ordered: bool = False

    @property
    def filtering_policies(self) -> list[FilteringPolicy]:
        """
        Get the ordered filtering policies list.

        The first call to this method sorts the list
        """
        if not self._is_filtering_policies_list_ordered:
            self._sort_filtering_policies_list()

        return self._filtering_policies

    @filtering_policies.setter
    def filtering_policies(self, value: list[FilteringPolicy]) -> None:
        self._filtering_policies = value

    def _sort_filtering_policies_list(self):
        filtering_policies_by_id = {
            filtering_policy.id: filtering_policy
            for filtering_policy in self._filtering_policies
        }

        non_first_filtering_policies_id = {
            filtering_policy.next_policy_id
            for filtering_policy in self._filtering_policies
            if filtering_policy.next_policy_id is not None
        }
        try:
            filtering_policy = [
                filtering_policy
                for filtering_policy in self._filtering_policies
                if filtering_policy.id not in non_first_filtering_policies_id
            ][0]
        except IndexError:
            filtering_policy = None
        ordered_filtering_policies = []

        while filtering_policy is not None:
            ordered_filtering_policies.append(filtering_policy)
            filtering_policy = (
                filtering_policy.next_policy_id
                and filtering_policies_by_id[filtering_policy.next_policy_id]
            )

        self._filtering_policies = ordered_filtering_policies
        self._is_filtering_policies_list_ordered = True

    def __eq__(self, value: object) -> bool:
        if value is None or not isinstance(value, Firewall):
            return False
        return (self.id, self.name, self.ip_address, self.port) == (
            value.id,
            value.name,
            value.ip_address,
            value.port,
        )

    def is_similar(self, other: Firewall) -> bool:
        """Check whether the objects are equals ignoring autogenerated attributes and relations."""
        return (self.name, self.ip_address, self.port) == (
            other.name,
            other.ip_address,
            other.port,
        )

    def convert_to_json(self, show_filtering_policies: bool = False) -> dict:
        result = {
            "id": self.id,
            "name": self.name,
            "ip_address": str(self.ip_address),
            "port": self.port,
        }

        if show_filtering_policies:
            result["filtering_policies"] = [
                filtering_policy.convert_to_json(show_firewall=False)
                for filtering_policy in self.filtering_policies
            ]

        return result

    def __repr__(self) -> str:
        return f"Firewall(id={self.id!r}, name={self.name!r}, ip_address={self.ip_address!r}, port={self.port!r})"
