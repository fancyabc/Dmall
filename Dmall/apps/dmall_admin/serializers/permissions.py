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
        fields = '__all__'  # ['id', 'username', 'mobile', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        user = super().create(validated_data)

        # 补齐 缺失的内容
        user.set_password(validated_data.get('password'))
        user.is_staff = True
        user.save()

        return user

    def update(self, instance, validated_data):
        # 调用父类实现数据更新
        super().update(instance, validated_data)

        password = validated_data.get('password')
        if password is not None:
            instance.set_password(password)
            instance.save()

        return instance
