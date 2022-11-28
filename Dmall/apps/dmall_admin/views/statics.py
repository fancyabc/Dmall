
from datetime import date
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import User


class DailyActiveAPIView(APIView):
    """日活跃用户统计"""
    def get(self, request):
        today = date.today()
        count = User.objects.filter(last_login__gte=today).count()

        return Response({'count': count})


class DailyOrderCountAPIView(APIView):
    """日下单用户量统计"""
    def get(self, request):
        today = date.today()
        count = User.objects.filter(orderinfo__create_time__gte=today).count()
        return Response({'count': count})


