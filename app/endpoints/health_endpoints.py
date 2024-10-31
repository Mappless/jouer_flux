from http import HTTPStatus

from flask import Response


def get_health():
    return Response(status=HTTPStatus.NO_CONTENT)
