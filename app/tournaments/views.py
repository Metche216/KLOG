from django.utils.translation import gettext as _

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from tournaments.serializers import TournamentSerializer, TEventSerializer, TournamentPlayerSerializer

from core.models import Tournament, TEvent, BasePlayer, TournamentPlayer, Team

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
        """ Check the ammount of players is according to the tournament standards and advances tevent status """
        tevent = self.get_object()

        if tevent.players.count() > 0 and tevent.players.count() % 4 == 0:
            serializer = self.get_serializer(tevent, data=request.data, partial=True, context={'request': request})
            tevent.advance()
            serializer = self.get_serializer(tevent)
        else:
            return Response(_('The total number of players must be a multiple of 4'), status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET','POST'])
    def team_build(self, request, pk=None):
        """ Create teams from the players received from the frontend """
        tevent = self.get_object()
        tevent_players = tevent.players
        if request.method == 'POST':
            teams = request.data
            if not isinstance(teams, dict):
                return Response({"error": _("player_ids must be a list")}, status=status.HTTP_400_BAD_REQUEST)
            for team_name,players in teams.items():
                if len(players) % 2 != 0:
                    return Response({"error": _("Number of players must be even to form teams")}, status=status.HTTP_400_BAD_REQUEST)
                player_a = TournamentPlayer.objects.get(id=players[0], tournament=tevent.tournament)
                player_b = TournamentPlayer.objects.get(id=players[1], tournament=tevent.tournament)
                new_team = Team.objects.create(name=team_name,tevent=tevent)
                new_team.players.add(player_a)
                new_team.players.add(player_b)
                new_team.save()

            return Response('Teams built', status=status.HTTP_201_CREATED)
        else:
            serializer = TournamentPlayerSerializer(tevent_players, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)