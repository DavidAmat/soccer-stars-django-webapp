from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from match import consumers

websocket_urlpatterns = [
    re_path(r"ws/match/(?P<room_match>\w+)/$", consumers.MatchConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})