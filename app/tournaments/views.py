from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from tournaments.serializers import TournamentSerializer, TEventSerializer

from core.models import Tournament, TEvent, BasePlayer, TournamentPlayer

class TournamentsViewset(viewsets.ModelViewSet):
    """ Viewset for the Tournaments API - allows all request methods """
    serializer_class = TournamentSerializer
    queryset = Tournament.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """ Instantiates and returns the list of permissions that this view requires. """
        if self.action != 'list':
            permission_classes = [IsAuthenticated]
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

    @action(detail=True, methods=['PATCH'])
    # path is created by hyphonated view's name > app:router-join-event ::: in stead of app:router-join_event
    # (url_path and url_name are valid params)
    def join_event(self, request, pk=None):
        """ Add or remove a player from the tournament event """
        tevent = self.get_object()
        serializer = self.get_serializer(tevent, data=request.data, partial=True, context={'request': request})

        user = request.user
        base_player = BasePlayer.objects.get(user=user)
        tplayer = TournamentPlayer.objects.get(player=base_player)


        if tplayer in tevent.players.all():
            tevent.players.remove(tplayer)
        else:
            tevent.players.add(tplayer)
        tevent.save()


        serializer = self.get_serializer(tevent)
        return Response(serializer.data)

    @action(detail=True, methods=['PATCH'])
    def start_tevent(self, request, pk=None):
        tevent = self.get_object()
        serializer = self.get_serializer(tevent, data=request.data, partial=True, context={'request': request})
        tevent.advance()
        serializer = self.get_serializer(tevent)
        return Response(serializer.data)
