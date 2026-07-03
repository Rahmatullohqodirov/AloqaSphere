from django.urls import path

from .views import (
    ConversationListView, ConversationDetailView, StartConversationView,
    SendMessageView, EndConversationView, MathSolveView,
)

urlpatterns = [
    path("conversations/", ConversationListView.as_view(), name="ai-conversation-list"),
    path("conversations/start/", StartConversationView.as_view(), name="ai-conversation-start"),
        path("conversations/<int:pk>/", ConversationDetailView.as_view(), name="ai-conversation-detail"),
    path("conversations/<int:pk>/message/", SendMessageView.as_view(), name="ai-conversation-message"),
    path("conversations/<int:pk>/end/", EndConversationView.as_view(), name="ai-conversation-end"),
    path("math/solve/", MathSolveView.as_view(), name="ai-math-solve"),
]
