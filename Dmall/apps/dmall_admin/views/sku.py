
from rest_framework.viewsets import ModelViewSet

from goods.models import SKU
from ..serializers.sku import SKUModelSerializer
from ..utils import PageNum


class SKUModelViewSet(ModelViewSet):

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return SKU.objects.filter(name__contains=keyword)

        return SKU.objects.all()

    serializer_class = SKUModelSerializer

    pagination_class = PageNum


# --------------- 三级分类数据 -----------------------

from goods.models import GoodsCategory
from rest_framework.generics import ListAPIView
from ..serializers.sku import GoodsCategoryModelSerializer


class GoodsCategoryAPIView(ListAPIView):

    queryset = GoodsCategory.objects.filter(subs=None)

    serializer_class = GoodsCategoryModelSerializer


# -------------------- SPU数据
from goods.models import SPU
from ..serializers.sku import SPUModelSerializer


class SPUListAPIView(ListAPIView):

    queryset = SPU.objects.all()

    serializer_class = SPUModelSerializer
