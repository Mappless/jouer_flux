from http import HTTPStatus
from typing import Optional

from flask import Response
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from app.db.models import FilteringPolicy, Firewall
from app.db.repositories import FilteringPolicyRepository, FirewallRepository
from app.validation.filtering_policy_models import PostFilteringPolicyModel
from app.validation.utils import translate_errors


def add_filtering_policy(firewall_id, body):
    try:
        post_filtering_policy_model = PostFilteringPolicyModel(**body)
    except ValidationError as err:
        return translate_errors(err.errors()), HTTPStatus.BAD_REQUEST

    firewall = FirewallRepository.find_by_id_with_filtering_policies(firewall_id)
    if firewall is None:
        return {
            "errors": [f"No firewall found with id '{firewall_id}'"]
        }, HTTPStatus.NOT_FOUND

    previous_filtering_policy = None
    if post_filtering_policy_model.previous_filtering_policy_id is not None:
        previous_filtering_policy = (
            FilteringPolicyRepository.find_by_firewall_id_and_id(
                firewall_id, post_filtering_policy_model.previous_filtering_policy_id
            )
        )

        if previous_filtering_policy is None:
            return {
                "errors": [
                    f"No filtering policy found with id '{post_filtering_policy_model.previous_filtering_policy_id}' on firewall with id '{firewall_id}'"
                ]
            }

    similar_filtering_policy = FilteringPolicyRepository.find_by_firewall_id_and_name(
        firewall_id, post_filtering_policy_model.name
    )

    if similar_filtering_policy:
        if _policy_has_different_position(
            firewall, previous_filtering_policy, similar_filtering_policy
        ):
            return {
                "errors": [
                    f"Filtering policy with name '{post_filtering_policy_model.name}' already exists on firewall with id '{firewall_id}'"
                ]
            }

        return similar_filtering_policy.convert_to_json(), HTTPStatus.CREATED

    if post_filtering_policy_model.previous_filtering_policy_id is None:
        filtering_policy = FilteringPolicyRepository.add_to_firewall_as_first_policy(
            firewall_id,
            FilteringPolicy(
                firewall_id=firewall_id, name=post_filtering_policy_model.name
            ),
        )
    else:
        filtering_policy = FilteringPolicyRepository.add_after_filtering_policy(
            previous_filtering_policy.id,
            FilteringPolicy(
                firewall_id=firewall_id, name=post_filtering_policy_model.name
            ),
        )

    return filtering_policy.convert_to_json(), HTTPStatus.CREATED


def _policy_has_different_position(
    firewall: Firewall,
    previous_filtering_policy: Optional[FilteringPolicy],
    filtering_policy: FilteringPolicy,
):
    if previous_filtering_policy is None:
        return firewall.filtering_policies[0] != filtering_policy

    return previous_filtering_policy.next_policy_id != filtering_policy.id


def get_filtering_policy(id: int, show_rules: bool = False):
    if show_rules:
        filtering_policy = FilteringPolicyRepository.find_by_id_with_rules(id)

        if filtering_policy is not None:
            return filtering_policy.convert_to_json(show_rules=True)

    try:
        return FilteringPolicyRepository.find_by_id(id).convert_to_json(), HTTPStatus.OK
    except NoResultFound:
        pass

    return {"errors": [f"No filtering policy found with id '{id}'"]}


def get_filtering_policies(firewall_id: int):
    firewall = FirewallRepository.find_by_id_with_filtering_policies(firewall_id)
    if firewall is None:
        return {
            "errors": [
                f"No filtering policy found with id '{firewall_id}' on firewall '{firewall_id}"
            ]
        }, HTTPStatus.NOT_FOUND

    return firewall.convert_to_json(show_filtering_policies=True), HTTPStatus.OK


def delete_filtering_policy(id: int):
    FilteringPolicyRepository.delete(id)

    return Response(status=HTTPStatus.NO_CONTENT)

