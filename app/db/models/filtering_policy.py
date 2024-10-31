from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .firewall import Firewall
    from .rule import Rule


class FilteringPolicy(Base):
    __tablename__ = "filtering_policy"
    __table_args__ = (UniqueConstraint("firewall_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    firewall_id: Mapped[int] = mapped_column(ForeignKey("firewall.id"))
    firewall: Mapped[Firewall] = relationship(
        back_populates="_filtering_policies", lazy="joined"
    )
    name: Mapped[str] = mapped_column(String(50))
    next_policy_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("filtering_policy.id")
    )
    _rules: Mapped[List[Rule]] = relationship(
        back_populates="filtering_policy", cascade="all, delete-orphan"
    )
    _is_rules_list_ordered: bool = False

    @property
    def rules(self) -> list[Rule]:
        """
        Get the ordered rules list.

        The first call to this method sorts the list
        """
        if not self._is_rules_list_ordered:
            self._sort_rules_list()

        return self._rules

    @rules.setter
    def rules(self, value: list[Rule]) -> None:
        self._rules = value

    def _sort_rules_list(self):
        rules_by_id = {rule.id: rule for rule in self._rules}

        non_first_rules_id = {
            rule.next_rule_id for rule in self._rules if rule.next_rule_id is not None
        }
        try:
            rule = [rule for rule in self._rules if rule.id not in non_first_rules_id][
                0
            ]
        except IndexError:
            rule = None
        ordered_rules = []

        while rule is not None:
            ordered_rules.append(rule)
            rule = rule.next_rule_id and rules_by_id[rule.next_rule_id]

        self._rules = ordered_rules
        self._is_rules_list_ordered = True

    def convert_to_json(
        self, show_firewall: bool = True, show_rules: bool = False
    ) -> dict:
        """
        Convert the object into a jsonifiable dict.

        :param show_firewall: Add the firewall in the json

        :return: A jsonifiable dict
        """
        result = {
            "id": self.id,
            "name": self.name,
        }

        if show_firewall:
            result["firewall"] = self.firewall.convert_to_json()

        if show_rules:
            result["rules"] = [rule.convert_to_json() for rule in self.rules]

        return result

    def __eq__(self, value: object) -> bool:
        if value is None or not isinstance(value, FilteringPolicy):
            return False
        return self.id == value.id
