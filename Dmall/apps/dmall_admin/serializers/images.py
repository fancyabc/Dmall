
from rest_framework import serializers
from fdfs_client.client import Fdfs_client

from goods.models import SKUImage, SKU


class SKUImageModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKUImage
        fields = '__all__'

    def update(self, instance, validated_data):
        """
            1. 创建Fdfs客户端
            2. 上传图片
            3. 根据上传结果进行判断,获取新图片的file_id
            4. 更新 模型的 image数据
        """
        image_data = validated_data.get('image').read()

        # 1. 创建Fdfs客户端
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 2. 上传图片
        result = client.upload_by_buffer(image_data)

        if result['Status'] != 'Upload successed.':
            raise serializers.ValidationError('上传失败,请稍后再试!')
        # 3. 根据上传结果进行判断,获取新图片的file_id
        file_id = result.get('Remote file_id')
        # 4. 更新 模型的 image数据
        instance.sku_id = validated_data.get('sku')
        instance.image = file_id
        instance.save()

        return instance


class ImageSKUModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id', 'name']
