# 当系统的功能 不能满足我们需求的时候就要重写

from django.contrib.auth import authenticate

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import time
from rest_framework import serializers

# 如果自定义了用户表，那么就要使用这个方法来获取用户模型
# 没有自定义的话可以使用以下方式加载用户模型:
from django.contrib.auth.models import User


# 重写TokenObtainPairSerializer类的部分方法以实现自定义数据响应结构和payload内容
# 管理员用户登录账号判断
class AdminJsonWebTokenSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        """
        此方法往token的有效负载 payload 里面添加数据
        例如自定义了用户表结构，可以在这里面添加用户邮箱，头像图片地址，性别，年龄等可以公开的信息
        这部分放在token里面是可以被解析的，所以不要放比较私密的信息
        :param user: 用戶信息
        :return: token
        """
        token = super().get_token(user)
        # 添加个人信息
        token['name'] = user.username
        return token

    def validate(self, attrs):
        """
        此方法为响应数据结构处理
        原有的响应数据结构无法满足需求，在这里重写结构如下：
        {
            "refresh": "xxxx.xxxxx.xxxxx",
            "access": "xxxx.xxxx.xxxx",
            "expire": Token有效期截止时间,
            "username": "用户名",
        }
        :param attrs: 請求參數
        :return: 响应数据

        # data是个字典
        # 其结构为：{'refresh': '用于刷新token的令牌', 'access': '用于身份验证的Token值'}
        """
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)  # 验证成功，返回一个User对象

            if user:
                if not user.is_active:  # 判断账户是否激活
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg)

                ###################################
                if not user.is_staff:   #
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg)

                ##################################

                data = {}

                # 获取Token对象
                refresh = self.get_token(user)
                data["refresh"] = str(refresh)
                # 加个token的键，值和access键一样
                data['token'] = str(refresh.access_token)
                # 令牌到期时间
                timestamp = refresh.access_token.payload['exp']  # 有效期-时间戳
                time_local = time.localtime(int(timestamp))
                data['expire'] = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

                # 用户名, id
                data['username'] = user.username
                data['id'] = user.id

                return data
            else:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg)
        else:   # 参数不全
            msg = 'Must include "{username_field}" and "password".'
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)
