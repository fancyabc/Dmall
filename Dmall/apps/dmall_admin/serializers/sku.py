from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from goods.models import SKU, GoodsCategory, SPU, SPUSpecification, SpecificationOption


class SKUModelSerializer(ModelSerializer):
    """
    前端传递的数据形式是
    caption: "12不想13香"
    category_id: 115            ~~~~~~
    cost_price: "1"
    is_launched: "true"
    market_price: "11"
    name: "13香"
    price: "1"
    specs: [{spec_id: "4", option_id: 8}, {spec_id: "5", option_id: 11}]
    spu_id: 2                   ~~~~~~~
    stock: "1"

    Q1. 外键中 spu和category的数据  前端是以 category_id 和 spu_id 的形式传递的 所以我们的序列化器 要改变
        spu_id=serializers.IntegerField()
        category_id=serializers.IntegerField()

    Q2. 我们 通过 添加 spu_id 和 category_id 能接收前端的数据,
        但是并没有改变 系统自动生成的  spu和category 这2个字段必传的选项
        如何去解决呢???
        ① 改为 required=False
        ② 为了配合查询数据的展示 我们 重写 spu 和category 这2个字段

        spu=serializers.StringRelatedField()
        category=serializers.StringRelatedField()

        新的疑问!!!  默认的字段是 required=True

        StringRelatedField 本质是 获取 关联模型的 __str__ 里的数据
    """
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    spu = serializers.StringRelatedField(required=False)
    category = serializers.StringRelatedField()

    class Meta:
        model = SKU
        fields = '__all__'


class GoodsCategoryModelSerializer(ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']


# ------SPU数据序列化器
class SPUModelSerializer(ModelSerializer):

    class Meta:
        model = SPU
        fields = ['id', 'name']


# --------------------SPU 规格和规格选项的序列化器

# 规格选项 序列化器
class OptionModelSerializer(ModelSerializer):

    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']


# SPU 规格 序列化器
class SpecsModelSerializer(ModelSerializer):

    options = OptionModelSerializer(many=True)

    class Meta:
        model = SPUSpecification
        fields = ['id', 'name', 'options']
