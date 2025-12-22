from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompetitionViewSet, ParticipantListCreateView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'competitions', CompetitionViewSet, basename='competition')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    
    # Custom path for getting participants of a specific competition
    path('competitions/<int:competition_id>/participants/', ParticipantListCreateView.as_view(), name='competition-participants'),
]