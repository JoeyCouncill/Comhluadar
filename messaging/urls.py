from django.urls import path
from messaging.views.inbox import inbox, chat_detail, mark_chat_seen

urlpatterns = [
	path('inbox/', inbox, name='inbox'),
    path("inbox/<int:chat_id>/", chat_detail, name="chat_detail"),
    path("inbox/<int:chat_id>/seen/", mark_chat_seen, name="mark_chat_seen"),
]
