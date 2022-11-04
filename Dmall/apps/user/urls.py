from django.urls import path
from .views import UsernameCountView, MobileCountView

urlpatterns = [
    # 判断用户名是否重复
    path('usernames/<username:username>/count/', UsernameCountView.as_view()),
    path('mobile/<mobile:mobile>/count/', MobileCountView.as_view()),
]
