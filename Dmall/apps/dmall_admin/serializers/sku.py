from rest_framework.serializers import ModelSerializer

from goods.models import SKU, GoodsCategory


class SKUModelSerializer(ModelSerializer):

    class Meta:
        model = SKU
        fields = '__all__'


class GoodsCategoryModelSerializer(ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']
