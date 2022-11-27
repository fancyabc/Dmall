from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path

from .views import MyTokenObtainPairView

urlpatterns = [
    path('authorizations/', MyTokenObtainPairView.as_view()),
]

