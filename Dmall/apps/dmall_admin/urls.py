from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path

urlpatterns = [
    path('authorizations/', TokenObtainPairView.as_view()),
]

