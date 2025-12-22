from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This delegates all 'api/' traffic to your app's urls.py
    path('api/', include('registration_and_settings.urls')),
]