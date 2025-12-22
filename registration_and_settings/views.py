from rest_framework import viewsets, generics, permissions
from django.shortcuts import get_object_or_404
from .models import Competition, Participant
from .serializers import CompetitionSerializer, ParticipantSerializer

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

class ParticipantListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list participants of a specific competition
    or add a new participant to it.
    """
    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        competition_id = self.kwargs['competition_id']
        return Participant.objects.filter(
            competition_id=competition_id, 
            competition__created_by=self.request.user
        )

    def perform_create(self, serializer):
        competition_id = self.kwargs['competition_id']
        competition = get_object_or_404(Competition, id=competition_id, created_by=self.request.user)
        serializer.save(competition=competition)