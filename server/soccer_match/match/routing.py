# match/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/match/(?P<room_name>\w+)/$", consumers.MatchConsumer.as_asgi()),
]