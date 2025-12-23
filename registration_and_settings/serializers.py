from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Competition, Participant, UserSettings

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ('theme', 'notifications_enabled')

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'full_name', 'age', 'unit_fellowship', 'email', 'access_code', 'status', 'score']
        read_only_fields = ['access_code', 'status', 'score']

class CompetitionSerializer(serializers.ModelSerializer):
    participant_count = serializers.IntegerField(source='participants.count', read_only=True)
    # This allows us to send a list of participants when creating a competition
    participants = ParticipantSerializer(many=True, required=False)

    class Meta:
        model = Competition
        fields = ['id', 'name', 'church_name', 'created_at', 'is_active', 'number_of_rounds', 'participant_count', 'participants']
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        participants_data = validated_data.pop('participants', [])
        # We get the user from the view's perform_create, but this is a safe fallback
        user = self.context['request'].user
        validated_data['created_by'] = user
        
        competition = Competition.objects.create(**validated_data)
        
        # Create any initial participants passed with the competition
        for participant_data in participants_data:
            Participant.objects.create(competition=competition, **participant_data)
            
        return competition