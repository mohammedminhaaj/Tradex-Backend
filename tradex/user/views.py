from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from .serializer import LoginSerializer
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import AuthenticationFailed
from tradex.utils import response_structure
from rest_framework.authtoken.models import Token

@api_view(["POST"])
def login_user(request: Request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        try:

            user = User.objects.get(username=username)
            authenticated = check_password(password, user.password)

            if not authenticated:
                raise AuthenticationFailed("Incorrect Password")
            
            token, _ = Token.objects.get_or_create(user=user)

            return response_structure("Login Successful", status.HTTP_200_OK, {"auth_token": token.key})
              
        except (User.DoesNotExist, AuthenticationFailed) as e:
            return response_structure("Invalid credentials", status.HTTP_404_NOT_FOUND if type(e) == User.DoesNotExist else status.HTTP_400_BAD_REQUEST)
        except Exception:
            return response_structure("Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return response_structure("Please fix the form errors", status.HTTP_400_BAD_REQUEST, serializer.errors)
        