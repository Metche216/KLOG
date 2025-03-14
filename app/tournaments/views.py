from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from tournaments.serializers import TournamentSerializer, TEventSerializer

from core.models import Tournament, TEvent

class TournamentsViewset(viewsets.ModelViewSet):
    """ Viewset for the Tournaments API - allows all request methods """
    serializer_class = TournamentSerializer
    queryset = Tournament.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self):
        """ Override Tournament creation for admin users only """
        pass
    def get_permissions(self):
        """ Instantiates and returns the list of permissions that this view requires. """
        if self.action != 'list':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class TEventViewset(viewsets.ModelViewSet):
    """ Views to manage the TEvents API """
    serializer_class = TEventSerializer
    queryset = TEvent.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """ Override the default ModelViewSet create method """
        serializer.save(created_by=self.request.user)

