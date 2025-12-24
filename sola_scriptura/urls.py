from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('registration_and_settings.urls')),
    path('api/game/', include('quiz_master.urls')),
]