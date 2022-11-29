from rest_framework.serializers import ModelSerializer

from goods.models import SKU, GoodsCategory, SPU, SPUSpecification, SpecificationOption


class SKUModelSerializer(ModelSerializer):

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
