from django.shortcuts import render

# Create your views here.

from django.views import View
from .models import User
from django.http import JsonResponse


class UsernameCountView(View):
    """判断用户名是否重复注册"""
    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'count': count, 'errmsg': 'ok'})
