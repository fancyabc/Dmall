from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path

from .views import dmall_token

urlpatterns = [
    path('authorizations/', dmall_token),
]

