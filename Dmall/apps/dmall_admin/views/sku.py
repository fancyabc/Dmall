
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
