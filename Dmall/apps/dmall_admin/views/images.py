from rest_framework.viewsets import ModelViewSet

from goods.models import SKUImage

from ..serializers.images import SKUImageModelSerializer
from ..utils import PageNum


class ImageModelViewSet(ModelViewSet):
    queryset = SKUImage.objects.all()

    serializer_class = SKUImageModelSerializer

    pagination_class = PageNum
