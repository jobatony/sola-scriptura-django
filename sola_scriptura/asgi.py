import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import quiz_master.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sola_scriptura.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            quiz_master.routing.websocket_urlpatterns
        )
    ),
})