from django.shortcuts import render

from django.http import JsonResponse
from django.views import View
from django.core.cache import cache

from .models import Area


class AreaView(View):

    def get(self, request):
        # 1 读取缓存数据
        province_list = cache.get('province')
        # 2 如果没有缓存，则查询数据库，并缓存数据
        if province_list is None:
            provinces = Area.objects.filter(parent=None)
            province_list = []

            for province in provinces:
                province_list.append({
                    'id': province.id,
                    'name': province.name
                })
            # 2.1 保存缓存数据
            cache.set('province', province_list, 24*3600)
        # 3.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'province_list': province_list})


class SubAreaView(View):

    def get(self, request, id):
        data_list = cache.get('city:%s'%id)
        if data_list is None:
            up_level = Area.objects.get(id=id)
            down_level = up_level.subs.all()

            data_list = []
            for item in down_level:
                data_list.append({
                    'id': item.id,
                    'name': item.name
                })
            cache.set('city:%s'%id, data_list, 24*3600)

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'sub_data': {'subs': data_list}})
