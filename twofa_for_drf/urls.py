from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from auth.urls import urlpatterns_auth
from auth.views import (
    PhoneVerificationView,
    PhoneRegistrationView,
    AuthyTokenVerifyView,
    CustomTokenObtainPairView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # 2FA
    path(
        "api/2fa/phone-verify/",
        PhoneVerificationView.as_view(),
        name="2fa_phone_verify",
    ),
    path(
        "api/2fa/phone-register/",
        PhoneRegistrationView.as_view(),
        name="2fa_register_phone",
    ),
    path(
        "api/2fa/token-verify/", AuthyTokenVerifyView.as_view(), name="2fa_token_verify"
    ),
    # JWT authentication uris for Rest Api
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Application Rest Api uris
    path("api/", include((urlpatterns_auth, "custom_auth"))),
]
