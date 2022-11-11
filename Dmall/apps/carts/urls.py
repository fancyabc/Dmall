from django.urls import path

from .views import CartsView, CartsSelectAllView, CartsSimpleView
urlpatterns = [
    path('carts/', CartsView.as_view()),
    path('carts/selection/', CartsSelectAllView.as_view()),
    path('carts/simple/', CartsSimpleView.as_view()),
]
