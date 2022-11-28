from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from goods.models import SKUImage

from ..serializers.images import SKUImageModelSerializer, ImageSKUModelSerializer
from ..utils import PageNum


class ImageModelViewSet(ModelViewSet):
    queryset = SKUImage.objects.all()

    serializer_class = SKUImageModelSerializer

    pagination_class = PageNum


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
