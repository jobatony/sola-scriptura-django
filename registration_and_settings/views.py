from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Import Token model
from rest_framework.authtoken.models import Token

from .models import Competition, Participant, UserSettings
from .serializers import CompetitionSerializer, ParticipantSerializer, UserSerializer, LoginSerializer, UserSettingsSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                login(request, user)
                # Generate or retrieve the token for this user
                token, created = Token.objects.get_or_create(user=user)
                
                return Response({
                    'token': token.key, # <--- Return this to React!
                    'user': UserSerializer(user).data
                })
            return Response({"error": "Invalid credentials"}, status=400)
        return Response(serializer.errors, status=400)

class LogoutView(APIView):
    def post(self, request):
        # Optional: Delete the token on logout to invalidate it
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        logout(request)
        return Response({"message": "Logged out successfully"})

class UserSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return UserSettings.objects.get_or_create(user=self.request.user)[0]

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
        
        # Check if data is a list (multiple) or dict (single)
        is_many = isinstance(request.data, list)
        
        serializer = ParticipantSerializer(data=request.data, many=is_many)
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