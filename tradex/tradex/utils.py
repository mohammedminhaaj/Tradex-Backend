from typing import Any, Dict, Optional
from rest_framework.response import Response

# Predefined messages for consistency across responses
SERVER_ERROR_MESSAGE = "Something went wrong!"
SUCCESS_MESSAGE = "Success"


def response_structure(
    message: str,
    code: int,
    data: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> Response:
    """
    Constructs a standardized response structure for API responses.

    Args:
        message (str): The message to include in the response.
        code (int): The HTTP status code for the response.
        data (Optional[Dict[str, Any]]): Optional dictionary containing additional data to include in the response.
        **kwargs (Any): Additional keyword arguments to include in the response.

    Returns:
        Response: A Response object with the structured data.
    """
    # Construct the base response dictionary
    response_dict = {
        "message": message,
        **kwargs
    }

    # Add data to the response dictionary if provided
    if data is not None:
        response_dict["data"] = data

    # Return the Response object with the structured data and status code
    return Response(data=response_dict, status=code)
