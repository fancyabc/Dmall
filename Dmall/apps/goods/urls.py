from django.urls import path
from .views import (
   IndexView, ListView, HotGoodsView,SKUSearchView
)

urlpatterns = [
    path('index/', IndexView.as_view()),
    path('list/<category_id>/skus/', ListView.as_view()),
    path('hot/<category_id>/', HotGoodsView.as_view()),
    path('search/', SKUSearchView()),   # 注意 没有as_view()

    # path('detail/<sku_id>/', DetailView.as_view()),
]
