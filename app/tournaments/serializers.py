from rest_framework import serializers

from core.models import Tournament

class TournamentSerializer(serializers.ModelSerializer):
    """ Tournament serializer """

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

    # In the serializer we define the methods that will be available