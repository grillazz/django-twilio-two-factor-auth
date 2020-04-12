from django.conf import settings

from authy.api import AuthyApiClient
import phonenumbers
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_204_NO_CONTENT,
    HTTP_206_PARTIAL_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_503_SERVICE_UNAVAILABLE,
)
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import CustomUserSerializer
from .serializers import (
    PhoneTokenSerializer,
    UserTokenSerializer,
    PhoneSerializer,
)


authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)


class CustomUserViewSet(ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing users.
    """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """

    2FA JWT Authentication: Step 0

    """

    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        ret = super().post(request, *args, **kwargs)
        user = CustomUser.objects.get(username=request.data["username"])
        # check if user has set to true any 2FA method
        # and needs to be re-direct to 2FA verification uri
        if user.is_twofa_on():
            # request 2FA token via sms for user
            sms = authy_api.users.request_sms(user.authy_id, {"force": True})
            if sms.ok():
                return Response(
                    {
                        "message": "SMS request successful. 2FA token verification expected."
                    },
                    status=HTTP_206_PARTIAL_CONTENT,
                )
            else:
                return Response(
                    {"error": sms.errors()["message"]},
                    status=HTTP_503_SERVICE_UNAVAILABLE,
                )
        return ret


class PhoneVerificationView(GenericAPIView):
    """

    2FA JWT Authentication: Step 1

    Twilio phone verification view.

    This endpoint will check if user mobile phone number is valid.
    If YES Twilio API send 4 digit verification token via SMS.

    """

    permission_classes = [IsAuthenticated]
    serializer_class = PhoneSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            return Response(status=HTTP_204_NO_CONTENT)


class PhoneRegistrationView(GenericAPIView):
    """

    2FA JWT Authentication: Step 2

    Twilio 2FA phone registration view.

    First it will validate if 4 digit tokend sent to user phone number is valid.
    If Twilio verification check pass in next step Twilio API call will register user for 2FA
    If success: user instance will be updated with verified phone number and received from Twilio API authy_id

    """

    serializer_class = PhoneTokenSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        phone = phonenumbers.parse(str(serializer.validated_data["authy_phone"]), None)
        authy_user = authy_api.users.create(
            user.email, str(phone.national_number), phone.country_code, True
        )
        if authy_user.ok():
            user.authy_id = authy_user.id
            user.authy_phone = serializer.validated_data["authy_phone"]
            user.save()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            return Response(authy_user.errors(), status=HTTP_400_BAD_REQUEST)


class AuthyTokenVerifyView(TokenObtainPairView):

    """

    2FA JWT Authentication: Step 3

    Twilio 2FA user authentication view.

    This view verify if Twilio 2FA registered user entered correct 8 digit token.
    Token will be requested by TwoFaTokenObtainPairView only for 2FA registered users

    Is success: user receive refresh and access JWT.

    """

    serializer_class = UserTokenSerializer

    def post(self, request, *args, **kwargs):
        ret = super().post(request, *args, **kwargs)
        user = CustomUser.objects.get(username=request.data["username"])
        # check if user has 2FA id assigned
        if user.is_twofa_on():
            # verify received 2FA token with Twilio API
            verification = authy_api.tokens.verify(
                user.authy_id, token=request.data["token"]
            )
            if verification.ok():
                # pass user instance to receive JWT
                return ret
            else:
                # return 2FA token verification error
                return Response(
                    {"error": verification.response.json()["errors"]["message"]},
                    status=HTTP_400_BAD_REQUEST,
                )
        else:
            # user has no 2FA authentication methods enabled
            return Response(
                {"error": "User not allowed for 2FA authentication."},
                status=HTTP_400_BAD_REQUEST,
            )
