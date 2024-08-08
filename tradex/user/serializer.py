from rest_framework.serializers import Serializer, CharField

class LoginSerializer(Serializer):
    username = CharField(min_length=6, max_length=128)
    password = CharField(min_length=6, max_length=128)