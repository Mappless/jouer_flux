import re

from pydantic_core import ErrorDetails


def translate_errors(errors: list[ErrorDetails]):
    """
    Translate pydantic errors into more readable ones.

    :param errors: result of ValidationError::errors function
    """
    return {
        "errors": [
            re.sub(r"^\w+", str(error["loc"][0]), error["msg"]) for error in errors
        ]
    }
