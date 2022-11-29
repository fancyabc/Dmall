from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.admintokenview import dmall_token
from .views.statics import *
from .views.user import *
from .views.images import *
from .views.sku import *

urlpatterns = [
    path('authorizations/', dmall_token),

    path('statistical/day_active/', DailyActiveAPIView.as_view()),  # 日活统计
    path('statistical/day_orders/', DailyOrderCountAPIView.as_view()),
    path('statistical/total_count/', UserTotalCountAPIView.as_view()),

    path('statistical/month_increment/', MonthCountAPIView.as_view()),

    path('users/', UserAPIView.as_view()),
    # 获取图片新增中的 sku展示
    path('skus/simple/', ImageSKUAPIView.as_view()),

    path('skus/categories/', GoodsCategoryAPIView.as_view()),

    # sku 中获取 spu的数据
    path('goods/simple/', SPUListAPIView.as_view()),
]


#  1.创建router实例
router = DefaultRouter()
# 2. 设置路由
router.register('skus/images', ImageModelViewSet, basename='images')
# 3.追加到 urlpatterns
urlpatterns += router.urls


# -------- sku

router.register(r'skus', SKUModelViewSet, basename='skus')
urlpatterns += router.urls
