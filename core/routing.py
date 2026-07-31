from django.urls import re_path
from core import consumer

websocket_urlpatterns = [
    re_path(r'ws/leaderboard/$', consumer.LeaderBoardConsumer.as_asgi()),
]