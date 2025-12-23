from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompetitionViewSet, ParticipantViewSet, RegisterView, LoginView, LogoutView, UserSettingsView

router = DefaultRouter()
# This creates /competitions/ (List/Create) and /competitions/{id}/ (Retrieve/Update/Delete)
router.register(r'competitions', CompetitionViewSet, basename='competition')
router.register(r'participants', ParticipantViewSet, basename='participant')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings/', UserSettingsView.as_view(), name='settings'),
    path('', include(router.urls)),
]