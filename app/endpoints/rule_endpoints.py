from http import HTTPStatus
from typing import Optional

from flask import Response
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from app.db.models import FilteringPolicy, Rule
from app.db.repositories import FilteringPolicyRepository, RuleRepository
from app.validation.rule_models import PostRuleModel
from app.validation.utils import translate_errors


def add_rule(filtering_policy_id: int, body: dict):
    try:
        post_rule_model = PostRuleModel(**body)
    except ValidationError as err:
        return translate_errors(err.errors()), HTTPStatus.BAD_REQUEST

    filtering_policy = FilteringPolicyRepository.find_by_id_with_rules(
        filtering_policy_id
    )

    if filtering_policy is None:
        return {
            "errors": [f"No filtering policy found with id '{filtering_policy_id}'"]
        }, HTTPStatus.NOT_FOUND

    previous_rule = None
    if post_rule_model.previous_rule_id is not None:
        previous_rule = RuleRepository.find_by_filtering_policy_id_and_id(
            filtering_policy_id, post_rule_model.previous_rule_id
        )

        if previous_rule is None:
            return {
                "errors": [
                    f"No rule found with id '{post_rule_model.previous_rule_id}' on filtering policy with id '{filtering_policy_id}'"
                ]
            }

    similar_rule = (
        RuleRepository.find_by_filtering_policy_id_source_destination_and_protocol(
            filtering_policy_id,
            post_rule_model.source_ip,
            post_rule_model.destination_ip,
            post_rule_model.destination_port,
            post_rule_model.protocol,
        )
    )

    rule = Rule(
        filtering_policy_id=filtering_policy_id,
        name=post_rule_model.name,
        source_ip=post_rule_model.source_ip,
        destination_ip=post_rule_model.destination_ip,
        destination_port=post_rule_model.destination_port,
        protocol=post_rule_model.protocol,
        action=post_rule_model.action,
    )
    if similar_rule:
        if similar_rule != rule or _rule_has_different_location(
            filtering_policy, previous_rule, similar_rule
        ):
            return {
                "errors": [
                    f"Rule with same source, destination and protocol already exists on filtering_policy with id '{filtering_policy_id}'"
                ]
            }
        return (
            similar_rule.convert_to_json(show_filtering_policy=True),
            HTTPStatus.CREATED,
        )

    if post_rule_model.previous_rule_id is None:
        rule = RuleRepository.add_to_filtering_policy_as_first_rule(
            filtering_policy_id, rule
        )
    else:
        rule = RuleRepository.add_after_rule(previous_rule.id, rule)

    return rule.convert_to_json(show_filtering_policy=True), HTTPStatus.CREATED


def _rule_has_different_location(
    filtering_policy: FilteringPolicy, previous_rule: Optional[Rule], rule: Rule
) -> bool:
    if previous_rule is None:
        return filtering_policy.rules[0] != rule

    return previous_rule.next_rule_id != rule.id


def get_rule(id: int):
    try:
        return RuleRepository.find_by_id(id).convert_to_json(show_filtering_policy=True)
    except NoResultFound:
        return {"errors": [f"No rule found with id '{id}'"]}, HTTPStatus.NOT_FOUND


def delete_rule(id: int):
    RuleRepository.delete(id)

    return Response(status=HTTPStatus.NO_CONTENT)
