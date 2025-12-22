from rest_framework import serializers
from .models import Competition, Participant, UserSettings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


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
    # Allow creating participants directly when creating a competition
    participants = ParticipantSerializer(many=True, required=False)

    class Meta:
        model = Competition
        fields = ['id', 'name', 'church_name', 'created_at', 'is_active', 'number_of_rounds', 'participant_count', 'participants']
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        participants_data = validated_data.pop('participants', [])
        # Get the user from the context (passed from the view)
        user = self.context['request'].user
        validated_data['created_by'] = user
        
        competition = Competition.objects.create(**validated_data)
        
        for participant_data in participants_data:
            Participant.objects.create(competition=competition, **participant_data)
            
        return competition