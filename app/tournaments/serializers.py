from django.utils import timezone
from django.utils.translation import gettext as _

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
        fields = ['id', 'name', 'sport', 'tournament', 'start_date','end_date']
        read_only_fields = ['id']

    def validate(self, data):
        """ Check that end_date is not before start_date. """
        start_date = data['start_date']
        end_date = data['end_date']

        if end_date < start_date:
            raise serializers.ValidationError(_("'End date' must be greater than or equal to 'start date'"))
        return data

    def create(self, validated_data):
        """ Create a tournament event """
        t = validated_data.pop('tournament')
        tevent = TEvent.objects.create(tournament=t, **validated_data)

        return tevent

    def update(self, instance, validated_data):
        """ Update the tevent """
        pass