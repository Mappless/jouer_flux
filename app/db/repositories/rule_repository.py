from ipaddress import IPv4Address
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from ..models import FilteringPolicy, Protocol, Rule
from ..session import Session


class RuleRepository:
    @staticmethod
    def add_to_filtering_policy_as_first_rule(filtering_policy_id: int, rule: Rule):
        with Session() as session:
            filtering_policy = session.scalar(
                select(FilteringPolicy)
                .outerjoin(FilteringPolicy._rules)
                .where(FilteringPolicy.id == filtering_policy_id)
            )

            try:
                former_first_rule = filtering_policy.rules[0]
            except IndexError:
                former_first_rule = None

            filtering_policy.rules = [rule] + filtering_policy.rules
            rule.next_rule_id = former_first_rule and former_first_rule.id

            session.commit()

        return rule

    @staticmethod
    def add_after_rule(previous_rule_id: int, rule: Rule) -> Rule:
        with Session() as session:
            previous_rule = session.scalar(
                select(Rule)
                .join(Rule.filtering_policy)
                .where(Rule.id == previous_rule_id)
            )
            previous_rule.filtering_policy._rules.append(rule)
            session.commit()  # To generate the new rule ID
            (previous_rule.next_rule_id, rule.next_rule_id) = (
                rule.id,
                previous_rule.next_rule_id,
            )
            session.commit()

        return rule

    @staticmethod
    def find_by_id(id: int):
        with Session() as session:
            return session.get_one(Rule, id)

    @staticmethod
    def find_by_filtering_policy_id_and_id(
        filtering_policy_id: int, id: int
    ) -> Optional[Rule]:
        with Session() as session:
            return session.scalar(
                select(Rule).where(
                    Rule.filtering_policy_id == filtering_policy_id, Rule.id == id
                )
            )

    @staticmethod
    def find_by_filtering_policy_id_source_destination_and_protocol(
        filtering_policy_id: int,
        source_ip: IPv4Address,
        destination_ip: IPv4Address,
        destination_port: int,
        protocol: Protocol,
    ) -> Optional[Rule]:
        with Session() as session:
            return session.scalar(
                select(Rule).where(
                    Rule.filtering_policy_id == filtering_policy_id,
                    Rule.source_ip == source_ip,
                    Rule.destination_ip == destination_ip,
                    Rule.destination_port == destination_port,
                    Rule.protocol == protocol,
                )
            )

    @staticmethod
    def delete(id: int) -> bool:
        """
        Delete a rule based on its id.

        :param id: The rule id

        :return: True if the rule was deleted, False if there was none
        """
        with Session() as session:
            try:
                previous_rule = session.scalar(
                    select(Rule).where(Rule.next_rule_id == id)
                )
                rule = session.get_one(Rule, id)

                if previous_rule is not None:
                    previous_rule.next_rule_id = rule.next_rule_id

                session.delete(rule)
                session.commit()

                return True
            except NoResultFound:
                return False
