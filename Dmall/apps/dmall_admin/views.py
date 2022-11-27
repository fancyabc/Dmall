from django.shortcuts import render

# Create your views here.
from rest_framework_simplejwt.views import TokenViewBase, TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .serializers import MyTokenSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    """
    自定义得到token username: 账号或者密码 password: 密码或者验证码
    """
    serializer_class = MyTokenSerializer


class MyTokenRefreshView(TokenViewBase):
    """
    自定义刷新token refresh: 刷新token的元素
    """
    serializer_class = TokenRefreshSerializer
