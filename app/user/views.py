from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings #needed for token auth

from .serializers import (
    UserSerializer,
    AuthTokenSerializer
    )

class CreateUserView(generics.CreateAPIView):
    """ View for creating a new user """
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """ View for obtaining a token """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ProfileView(generics.RetrieveUpdateAPIView):
    """ View for displaying and updating user personal info """
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
