from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import Permission, ContentType, Group


class PermissionModelSerializer(ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


# --------------------------ContentType
class ContentTypeModelSerializer(ModelSerializer):

    class Meta:
        model = ContentType
        fields = ['id', 'name']


# ---------------------------------------组
class GroupModelSerializer(ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


# ____________________ 普通管理员序列化器 _______________
from user.models import User


class AdminUserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email']
