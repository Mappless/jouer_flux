from http import HTTPStatus
from ipaddress import IPv4Address

from flask import Response
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from app.db.models import Firewall
from app.db.repositories import FirewallRepository
from app.validation.firewall_models import PostFirewallModel
from app.validation.utils import translate_errors


def add_firewall(body: dict):
    try:
        PostFirewallModel(**body)
    except ValidationError as err:
        return translate_errors(err.errors()), HTTPStatus.BAD_REQUEST

    same_id_and_port_firewall = FirewallRepository.find_by_ip_address_and_port(
        body["ip_address"], body["port"]
    )

    if same_id_and_port_firewall is None:
        return (
            FirewallRepository.add(Firewall(**body)).convert_to_json(),
            HTTPStatus.CREATED,
        )
    elif not same_id_and_port_firewall.is_similar(
        Firewall(
            name=body["name"],
            ip_address=IPv4Address(body["ip_address"]),
            port=body["port"],
        )
    ):
        return {
            "errors": ["A firewall with this address and port already exists"]
        }, HTTPStatus.BAD_REQUEST

    return same_id_and_port_firewall.convert_to_json(), HTTPStatus.CREATED


def get_firewall(id: int):
    try:
        return FirewallRepository.find_by_id(id).convert_to_json(), HTTPStatus.OK
    except NoResultFound:
        return {"errors": [f"No firewall found with id '{id}'"]}, HTTPStatus.NOT_FOUND


def delete_firewall(id: int):
    FirewallRepository.delete(id)

    return Response(status=HTTPStatus.NO_CONTENT)
