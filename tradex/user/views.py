from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from .serializer import LoginSerializer
from tradex.utils import response_structure, SERVER_ERROR_MESSAGE


@api_view(["POST"])
def login_user(request: Request) -> Response:
    """
    Handle user login by validating username and password, and issuing an authentication token.

    Args:
        request (Request): The HTTP request object containing login credentials.

    Returns:
        Response: A Response object with a status code and message indicating success or failure.
    """
    # Initialize the serializer with request data
    serializer = LoginSerializer(data=request.data)

    # Validate the serializer data
    if serializer.is_valid():
        username: str = serializer.validated_data["username"]
        password: str = serializer.validated_data["password"]

        try:
            # Attempt to retrieve the user by username
            user = User.objects.get(username=username)

            # Check if the provided password is correct
            authenticated: bool = check_password(password, user.password)
            if not authenticated:
                raise AuthenticationFailed("Incorrect Password")

            # Get or create an authentication token for the user
            token, _ = Token.objects.get_or_create(user=user)

            # Return a successful response with the authentication token
            return response_structure("Login Successful", status.HTTP_200_OK, {"auth_token": token.key})

        except User.DoesNotExist:
            # Handle case where the user does not exist
            return response_structure("Invalid credentials", status.HTTP_404_NOT_FOUND)
        except AuthenticationFailed:
            # Handle case where authentication failed due to incorrect password
            return response_structure("Invalid credentials", status.HTTP_400_BAD_REQUEST)
        except Exception:
            # Handle any other unexpected errors
            return response_structure(SERVER_ERROR_MESSAGE, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Return error response if serializer data is not valid
    return response_structure("Please fix the form errors", status.HTTP_400_BAD_REQUEST, serializer.errors)
