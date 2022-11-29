
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


# ---   SPU 规格和规格选项 数据

"""
SPU --> SPUSpecification(商品SPU规格) -->SpecificationOption(规格选项)

需求:
    当我们选择不同的 spu的时候 ,前端会发送axios请求,将spu_id 发送给我们
    我们需要根据spu_id 查询 商品SPU规格.  还需要根据SPU规格 获取 对应的(规格)选项信息

    1. spu_id
    2. 获取商品SPU规格
    3. 根据spu规格 获取 对应选项信息
"""
from rest_framework.views import APIView
from rest_framework.response import Response

from goods.models import SPUSpecification,SpecificationOption
from ..serializers.sku import SpecsModelSerializer


class SPUSpecAPIView(APIView):

    def get(self, request, spu_id):
        # 1. spu_id
        # 2. 获取商品SPU规格
        specs = SPUSpecification.objects.filter(spu_id=spu_id)
        # 3. 根据spu规格 获取 对应选项信息
        # for spec in specs:
        #     options=SpecificationOption.objects.filter(spec=spec)

        # 创建序列化器
        serializer = SpecsModelSerializer(specs, many=True)
        # 返回响应
        return Response(serializer.data)
