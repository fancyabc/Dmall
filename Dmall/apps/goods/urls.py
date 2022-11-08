from django.urls import path
from .views import (
   IndexView, ListView, HotGoodsView,
)

urlpatterns = [
    path('index/', IndexView.as_view()),
    path('list/<category_id>/skus/', ListView.as_view()),
    path('hot/<category_id>/', HotGoodsView.as_view()),
]
