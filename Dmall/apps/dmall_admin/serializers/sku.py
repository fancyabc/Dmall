from rest_framework.serializers import ModelSerializer

from goods.models import SKU, GoodsCategory, SPU


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