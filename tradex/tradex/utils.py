from typing import Any
from rest_framework.response import Response

def response_structure(message: str, code: int, data: dict[str, Any] | None = None) -> Response:
    response_dict = {
        "message": message
    }
    if data:
        response_dict["data"] = data
    return Response(data=response_dict, status=code)