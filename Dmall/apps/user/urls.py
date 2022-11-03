from django.urls import path
from .views import UsernameCountView

urlpatterns = [
    # 判断用户名是否重复
    path('usernames/<username>/count/', UsernameCountView.as_view()),
]