from datetime import timedelta
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


"""

1. 获取今天的日期
2. 往前回退30天
3. 遍历查询数据

    例如: 10-01  到 10-2 数据
    3.1 获取区间开始的日期
    3.2 获取区间结束的日期
    3.3 查询
    3.4 把查询的数据放入列表中
"""


class MonthCountAPIView(APIView):

    def get(self, request):
        # 1. 获取今天的日期
        today = date.today()
        # 2. 往前回退30天
        before_date = today - timedelta(days=30)
        data = []
        # 3. 遍历查询数据
        for i in range(30):
            # i=0
            #
            #     例如: 10-01  到 10-2 数据
            #     3.1 获取区间开始的日期
            start_date = before_date + timedelta(days=i)
            #     3.2 获取区间结束的日期
            end_date = before_date + timedelta(days=(i + 1))
            #     3.3 查询
            count = User.objects.filter(date_joined__gte=start_date,
                                        date_joined__lt=end_date).count()
            #     3.4 把查询的数据放入列表中
            data.append({
                'count': count,
                'date': start_date
            })

        return Response(data)
