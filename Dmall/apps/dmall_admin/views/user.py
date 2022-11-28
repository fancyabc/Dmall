"""
用户管理

    用户展示    --  获取用户信息,实现分页和搜索功能
        1. 先实现用户查询
            1.1 查询所有用户
            1.2 将对象列表转换为 满足需求的字典列表 (序列化器)
            1.3 返回响应
        2. 再实现搜索功能
        3. 最后实现分页
"""
from collections import OrderedDict
from rest_framework.generics import ListAPIView
from user.models import User
from ..serializers.user import UserModelSerializer
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response


class PageNum(PageNumberPagination):
    # 1.开启分页
    # 2.设置默认每页多少条记录
    page_size = 5

    # 开启 每页多少条记录 可以通过传递的参数传递
    # pagesize=xxx 每页多少条记录的 key
    page_size_query_param = 'pagesize'
    max_page_size = 20  # 最大一页多少条记录

    # 重写分页返回方法，按照指定的字段进行分页数据返回
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('lists', data),
            ('page', self.page.number),
            ('pages', self.page.paginator.num_pages),
            ('pagesize', self.page.paginator.per_page)
        ]))


class UserAPIView(ListAPIView):

    queryset = User.objects.all()

    serializer_class = UserModelSerializer

    pagination_class = PageNum
