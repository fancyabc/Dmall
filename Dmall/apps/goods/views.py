
from collections import OrderedDict
from django.shortcuts import render
from django.views import View

from contents.models import ContentCategory
from utils.goods import get_categories


class IndexView(View):
    """首页广告"""

    def get(self, request):
        """提供首页广告界面"""
        # 查询商品频道和分类
        categories = get_categories()

        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request, 'index.html', context=context)
