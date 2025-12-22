from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/competition/(?P<competition_id>\w+)/$', consumers.CompetitionConsumer.as_asgi()),
]