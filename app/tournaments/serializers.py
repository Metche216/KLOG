from django.utils import timezone
from django.utils.translation import gettext as _

from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from core.models import Tournament, TEvent, TournamentPlayer, BasePlayer

class TournamentSerializer(serializers.ModelSerializer):
    """ Tournament serializer """

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

    # In the serializer we define the methods that will be available


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
        queryset=BasePlayer.objects.all(),  # Importante: Define el queryset
        required=False
    )

    class Meta:
        model = TEvent
        fields = ['id', 'name', 'sport', 'tournament', 'start_date','end_date', 'players']
        read_only_fields = ['id']

    def _get_or_create_tournament_player(self, tevent, base_player):
        """ Returns the tournament player for each base player invited """

        player_obj, created = TournamentPlayer.objects.get_or_create(player=base_player, tournament=tevent.tournament)
        if created:
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
        """Update recipe."""
        # Basic configuration for updating through serializer, loop through the values of the validated data and set them in the instance.
        players = validated_data.pop('players',None)

        if players is not None:
            for player in players:
                self._get_or_create_tournament_player(instance, player)


        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
