

from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission
from ..serializers.permissions import PermissionModelSerializer
from ..utils import PageNum


class PermissionModelViewSet(ModelViewSet):

    queryset = Permission.objects.all()
    serializer_class = PermissionModelSerializer

    pagination_class = PageNum


