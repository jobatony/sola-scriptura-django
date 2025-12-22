from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Competition, Participant
from .serializers import CompetitionSerializer, ParticipantSerializer

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "username": user.username})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)

class CompetitionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows competitions to be viewed or edited.
    Only shows competitions created by the logged-in moderator.
    """
    serializer_class = CompetitionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Competition.objects.filter(created_by=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_participants(self, request, pk=None):
        """Custom action to add participants to an existing competition"""
        competition = self.get_object()
        serializer = ParticipantSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save(competition=competition)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ParticipantViewSet(viewsets.ModelViewSet):
    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show participants from competitions owned by the user
        return Participant.objects.filter(competition__created_by=self.request.user)