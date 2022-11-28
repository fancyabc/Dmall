"""
用户管理

    用户展示    --  获取用户信息,实现分页和搜索功能
        1. 先实现用户查询
            1.1 查询所有用户
            1.2 将对象列表转换为 满足需求的字典列表 (序列化器)
            1.3 返回响应
        2. 再实现搜索功能
                es - elasticsearch
                模糊查询

                获取 keyword
                根据 keywork 进行 模糊查询
        3. 最后实现分页
"""

from rest_framework.generics import ListAPIView, ListCreateAPIView
from user.models import User
from ..serializers.user import UserModelSerializer
from ..utils import PageNum


class UserAPIView(ListCreateAPIView):
    # 设置方法  def get_queryset(self): 根据  不同的业务逻辑返回不同的查询结果集
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return User.objects.filter(username__contains=keyword)
        return User.objects.all()

    serializer_class = UserModelSerializer

    pagination_class = PageNum
