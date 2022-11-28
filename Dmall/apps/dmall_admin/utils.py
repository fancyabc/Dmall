from collections import OrderedDict
from rest_framework.pagination import PageNumberPagination
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
