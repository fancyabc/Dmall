from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from goods.models import SKUImage

from ..serializers.images import SKUImageModelSerializer, ImageSKUModelSerializer
from ..utils import PageNum


class ImageModelViewSet(ModelViewSet):
    queryset = SKUImage.objects.all()

    serializer_class = SKUImageModelSerializer

    pagination_class = PageNum

    def create(self, request, *args, **kwargs):
        """
        1.接收数据
        2.验证数据
        3.保存数据(保存 file_id 和sku_id)
         3.1 创建 Fdfs的客户端
         3.2 上传图片
         3.3 根据上传的结果 获取file_id
         3.4 保存SKUImage
        4.返回响应
        """

        image = request.data.get('image')
        image_data = image.read()   # read() 方法来读取二进制图片流

        # 1.接收数据
        sku_id = request.data.get('sku')
        # 2 验证数据
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # 3 保存数据(保存 file_id 和sku_id)
        # 3.1 创建 Fdfs的客户端
        from fdfs_client.client import Fdfs_client
        client = Fdfs_client('utils/fastdfs/client.conf')

        # 3.2 上传图片
        result = client.upload_by_buffer(image_data)  # 我们上传图片的二进制流 因为客户端提交图片的时候 上传的图片是二进制流
        """
            {
            'Remote file_id': 'group1/M00/00/00/wKjlhFsTgJ2AJvG_AAAyZgOTZN0850.jpg', 
            'Uploaded size': '12.00KB',
             'Local file name': '/home/python/Desktop/images/0.jpg',
              'Storage IP': '192.168.229.132',
              'Group name': 'group1', 
              'Status': 'Upload successed.'
              }
        """
        # 3.3 根据上传的结果 获取file_id
        if result['Status'] != 'Upload successed.':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        file_id = result.get('Remote file_id')
        # 3.4 保存SKUImage
        image_new = SKUImage.objects.create(
            sku_id=sku_id,
            image=file_id
        )

        # 4.返回响应
        return Response({
            'id': image_new.id,
            'sku': sku_id,
            'image': image_new.image.url
        }, status=status.HTTP_201_CREATED)


# ----------------- 获取所有sku -----------------
from goods.models import SKU
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin


class ImageSKUAPIView(ListModelMixin, GenericAPIView):
    queryset = SKU.objects.all()

    serializer_class = ImageSKUModelSerializer

    def get(self, request):
        return self.list(request)
        # skus = self.get_queryset()
        #
        # serializer = self.get_serializer(skus, many=True)
        # return Response(serializer.data)
