from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

from ..models import FilteringPolicy, Firewall
from ..session import Session


class FilteringPolicyRepository:
    @staticmethod
    def add_to_firewall_as_first_policy(
        firewall_id: int, filtering_policy: FilteringPolicy
    ) -> FilteringPolicy:
        with Session() as session:
            firewall = session.scalar(
                select(Firewall)
                .outerjoin(Firewall._filtering_policies)
                .where(Firewall.id == firewall_id)
            )

            try:
                former_first_filtering_policy = firewall.filtering_policies[0]
            except IndexError:
                former_first_filtering_policy = None

            firewall.filtering_policies = [
                filtering_policy
            ] + firewall.filtering_policies
            filtering_policy.next_policy_id = former_first_filtering_policy

            session.commit()

        return filtering_policy

    @staticmethod
    def add_after_filtering_policy(
        previous_filtering_policy_id: int, filtering_policy: FilteringPolicy
    ) -> FilteringPolicy:
        with Session() as session:
            previous_filtering_policy = session.scalar(
                select(FilteringPolicy)
                .join(FilteringPolicy.firewall)
                .where(FilteringPolicy.id == previous_filtering_policy_id)
            )
            previous_filtering_policy.firewall._filtering_policies.append(
                filtering_policy
            )
            session.commit()  # To generate the new filtering policy ID
            (
                previous_filtering_policy.next_policy_id,
                filtering_policy.next_policy_id,
            ) = (filtering_policy.id, previous_filtering_policy.next_policy_id)
            session.commit()

        return filtering_policy

    @staticmethod
    def find_by_firewall_id_and_name(
        firewall_id: int, name: str
    ) -> Optional[FilteringPolicy]:
        with Session() as session:
            return session.scalar(
                select(FilteringPolicy).where(
                    FilteringPolicy.firewall_id == firewall_id,
                    FilteringPolicy.name == name,
                )
            )

    @staticmethod
    def find_by_firewall_id_and_id(
        firewall_id: int, id: int
    ) -> Optional[FilteringPolicy]:
        with Session() as session:
            return session.scalar(
                select(FilteringPolicy).where(
                    FilteringPolicy.id == id, FilteringPolicy.firewall_id == firewall_id
                )
            )

    @staticmethod
    def find_by_id(id: int) -> FilteringPolicy:
        """
        Find a filtering policy thanks to its id.

        :param id: The filtering policy's id

        :raise NoResultFound: if there is no filtering policy with this id
        """
        with Session() as session:
            return session.get_one(FilteringPolicy, id)

    @staticmethod
    def find_by_id_with_rules(id: int) -> Optional[FilteringPolicy]:
        with Session() as session:
            return session.scalar(
                select(FilteringPolicy)
                .where(FilteringPolicy.id == id)
                .options(joinedload(FilteringPolicy._rules))
            )

    @staticmethod
    def delete(id: int) -> bool:
        """
        Delete a filtering policy based on its id.

        :param id: The filtering policy's id

        :return: True if the filtering policy was deleted, False if there was none
        """
        with Session() as session:
            try:
                previous_filtering_policy = session.scalar(
                    select(FilteringPolicy).where(FilteringPolicy.next_policy_id == id)
                )
                filtering_policy = session.get_one(FilteringPolicy, id)

                if previous_filtering_policy is not None:
                    previous_filtering_policy.next_policy_id = (
                        filtering_policy.next_policy_id
                    )

                session.delete(filtering_policy)
                session.commit()

                return True
            except NoResultFound:
                return False

