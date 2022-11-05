from django.urls import path
from .views import QQLoginURLView

urlpatterns = [
    path('qq/authorization/', QQLoginURLView.as_view()),
]
