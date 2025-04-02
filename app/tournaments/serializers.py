from django.utils import timezone
from django.utils.translation import gettext as _

from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from core.models import Tournament, TEvent, TournamentPlayer, BasePlayer

class TournamentSerializer(serializers.ModelSerializer):
    """ Tournament serializer """

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'description', 'players', 'teams_n']
        read_only_fields = ['id']

    # In the serializer we define the methods that will be available
    def _create_tournament_players(self, tournament, players):
        """ Helper function for creating TPlayers for the tournament """
        for player in players:
            TournamentPlayer.objects.create(tournament=tournament, player=player)
            tournament.players.add(player)


    def create(self, validated_data): #POST request
        """ Create a tournament event """
        players = validated_data.pop('players', None)
        tournament = Tournament.objects.create( **validated_data)
        self._create_tournament_players(tournament, players)
        return tournament

    def update(self, instance, validated_data): # PUT/PATCH request
        players = validated_data.pop('players', None)

        self._create_tournament_players(instance, players)
        instance.save()

        return instance

class TournamentPlayerSerializer(serializers.ModelSerializer):
    """ Serializer for the tournament players"""
    class Meta:
        model = TournamentPlayer
        fields = ['id', 'player', 'tournament']
        read_only_fields = ['id']



class TEventSerializer(serializers.ModelSerializer):
    """Tournament Events Serializer"""
    players = PrimaryKeyRelatedField(
        many=True,
        queryset=TournamentPlayer.objects.all(),  # Importante: Define el queryset
        required=False
    )

    class Meta:
        model = TEvent
        fields = ['id', 'name', 'sport', 'tournament', 'start_date','end_date', 'players']
        read_only_fields = ['id']

    def _get_or_create_tournament_player(self, tevent, base_player):
        """ Returns the tournament player for each base player invited """

        player_obj, created = TournamentPlayer.objects.get_or_create(player=base_player, tournament=tevent.tournament)
        tevent.players.add(player_obj)


    def validate(self, data):
        """ Validate serializer data before processing """

        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(_("'End date' must be greater than or equal to 'start date'"))
        return data

    def create(self, validated_data):
        """ Create a tournament event """
        t = validated_data.pop('tournament')
        tevent = TEvent.objects.create(tournament=t, **validated_data)

        return tevent

    def update(self, instance, validated_data):
        """ Update tevent """
        # Basic configuration for updating through serializer, loop through the values of the validated data and set them in the instance.
        players = validated_data.pop('players',None)
        
        # Logic to subscribe or remove player from tevent: if in list, remove, if not in list, add. 
        if players is not None:
            for player in players:
                if player not in instance.players.all():
                    instance.players.add(player)
                else:
                    instance.players.remove(player)


        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
