from django.urls import path
from .views import (
    SignupView,VerifySetUpAccount,DomainVerifyingView,UserLoginView,KeycloakGroupView
)

urlpatterns = [
    path('client/signup', SignupView.as_view()),
    path('verify/account/<str:token>', VerifySetUpAccount.as_view()),
    path('verify/account', VerifySetUpAccount.as_view()),
    path('check/subdomain', DomainVerifyingView.as_view()),
    path('login/user', UserLoginView.as_view()),
    path('group', KeycloakGroupView.as_view()),
]