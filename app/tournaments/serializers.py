from django.utils import timezone

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
        fields = ['id', 'name', 'sport', 'tournament', 'start_date']
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a tournament event """
        t = validated_data.pop('tournament')
        start = validated_data.pop('start_date',None)
        end = validated_data.pop('end_date',None)
        tevent = TEvent.objects.create(tournament=t, start_date=start, **validated_data)
        if start is None:
            tevent.start_date = timezone.now()
        return tevent