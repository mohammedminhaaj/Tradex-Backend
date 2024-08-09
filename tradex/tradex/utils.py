from typing import Any
from rest_framework.response import Response

SERVER_ERROR_MESSAGE = "Something went wrong!"
SUCCESS_MESSAGE = "Success"

def response_structure(message: str, code: int, data: dict[str, Any] | None = None) -> Response:
    response_dict = {
        "message": message
    }
    if data:
        response_dict["data"] = data
    return Response(data=response_dict, status=code)