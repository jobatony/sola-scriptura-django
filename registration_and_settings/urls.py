from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompetitionViewSet, ParticipantViewSet, LoginView

router = DefaultRouter()
router.register(r'competitions', CompetitionViewSet, basename='competition')
router.register(r'participants', ParticipantViewSet, basename='participant')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]