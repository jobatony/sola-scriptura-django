from rest_framework import serializers
from .models import Competition, Participant

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'full_name', 'age', 'unit_fellowship', 'email', 'access_code', 'status', 'score']
        read_only_fields = ['access_code', 'status', 'score']

class CompetitionSerializer(serializers.ModelSerializer):
    participant_count = serializers.IntegerField(source='participants.count', read_only=True)

    class Meta:
        model = Competition
        fields = ['id', 'name', 'church_name', 'created_at', 'is_active', 'number_of_rounds', 'participant_count']
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)