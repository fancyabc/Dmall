from django.urls import path
from .views import (
    UsernameCountView, MobileCountView, RegisterView,
    LoginView, LogoutView, CenterView, EmailView, VerifyEmailView,
    AddressCreateView, AddressView, UpdateDestroyAddressView,
    DefaultAddressView, UpdateTitleAddressView, UserHistoryView
)

urlpatterns = [
    # 判断用户名是否重复
    path('usernames/<username:username>/count/', UsernameCountView.as_view()),
    path('mobiles/<mobile:mobile>/count/', MobileCountView.as_view()),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('info/', CenterView.as_view()),
    path('emails/', EmailView.as_view()),
    path('emails/verification/', VerifyEmailView.as_view()),
    path('addresses/create/', AddressCreateView.as_view()),
    path('addresses/', AddressView.as_view()),
    path('addresses/<address_id>/', UpdateDestroyAddressView.as_view()),
    path('addresses/<address_id>/default/', DefaultAddressView.as_view()),
    path('addresses/<address_id>/title/', UpdateTitleAddressView.as_view()),

    path('browse_histories/', UserHistoryView.as_view()),
]
