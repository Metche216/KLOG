from rest_framework import serializers

from core.models import Tournament, TEvent

class TournamentSerializer(serializers.ModelSerializer):
    """ Tournament serializer """

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

    # In the serializer we define the methods that will be available

class TEventSerializer(serializers.ModelSerializer):
    """ Tournament Events Serializer"""

    class Meta:
        model = TEvent
        fields = ['id', 'name', 'sport', 'tournament']
        
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a tournament event """
        tournament = validated_data['tournament']
        print(tournament)
        t = Tournament.objects.get(name=tournament)
        validated_data.pop('tournament')
        tevent = TEvent.objects.create(tournament=t, **validated_data)
        return tevent