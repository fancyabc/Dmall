
from rest_framework import serializers

from goods.models import SKUImage


class SKUImageModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKUImage
        fields = '__all__'
