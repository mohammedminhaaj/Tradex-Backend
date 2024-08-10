from rest_framework.serializers import Serializer, CharField


class LoginSerializer(Serializer):
    """
    Serializer for user login, handling validation of username and password fields.

    Attributes:
        username (CharField): The username field with a minimum length of 6 and maximum length of 128 characters.
        password (CharField): The password field with a minimum length of 6 and maximum length of 128 characters.
    """

    username = CharField(min_length=6, max_length=128)
    password = CharField(min_length=6, max_length=128)
