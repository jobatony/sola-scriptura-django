import os
import django
from django.core.asgi import get_asgi_application

# 1. Set the settings module (CHANGE 'myproject' to your actual project name)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sola_scriptura.settings')

# 2. Initialize Django EARLY
# This prevents "AppRegistryNotReady" errors when importing consumers later
django.setup() 

# 3. Import Channels logic AFTER django.setup()
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

# 4. Import your app's routing
import quiz_master.routing

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": get_asgi_application(),

    # WebSocket handler
    "websocket": AuthMiddlewareStack(
        URLRouter(
            quiz_master.routing.websocket_urlpatterns
        )
    ),
})