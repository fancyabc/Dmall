

from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission
from ..serializers.permissions import PermissionModelSerializer
from ..utils import PageNum


class PermissionModelViewSet(ModelViewSet):

    queryset = Permission.objects.all()
    serializer_class = PermissionModelSerializer

    pagination_class = PageNum


# ------------------ ContentType 权限类型 ------------------
"""
所谓的权限 其实就是 对于模型的增删改查操作
我们需要确定对哪个模型 有 增删改查的权限
"""
from django.contrib.auth.models import ContentType
from rest_framework.generics import ListAPIView
from ..serializers.permissions import ContentTypeModelSerializer


class ContentTypeListAPIView(ListAPIView):

    queryset = ContentType.objects.all().order_by('id')
    serializer_class = ContentTypeModelSerializer
