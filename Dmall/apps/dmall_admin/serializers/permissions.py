from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import Permission


class PermissionModelSerializer(ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'
