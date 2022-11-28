from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path

from .views.admintokenview import dmall_token
from .views.statics import *

urlpatterns = [
    path('authorizations/', dmall_token),

    path('statistical/day_active/', DailyActiveAPIView.as_view()),  # 日活统计
    path('statistical/day_orders/', DailyOrderCountAPIView.as_view()),
    path('statistical/total_count/', UserTotalCountAPIView.as_view()),

    path('statistical/month_increment/', MonthCountAPIView.as_view()),
]

