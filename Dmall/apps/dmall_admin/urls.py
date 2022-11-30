from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.admintokenview import dmall_token
from .views.statics import *
from .views.user import *
from .views.images import *
from .views.sku import *
from .views.permissions import PermissionModelViewSet, ContentTypeListAPIView

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
    # sku 中获取 spu的规格和规格选项
    path('goods/<spu_id>/specs/', SPUSpecAPIView.as_view()),

    # 权限中 获取 ContentType 的数据
    path('permission/content_types/', ContentTypeListAPIView.as_view()),
]


#  1.创建router实例
router = DefaultRouter()
# 2. 设置路由
router.register('skus/images', ImageModelViewSet, basename='images')
# 3.追加到 urlpatterns


# -------- sku

router.register('skus', SKUModelViewSet, basename='skus')


# ---- 权限
router.register('permission/perms', PermissionModelViewSet, basename='perms')
urlpatterns += router.urls
