from django.conf import settings

from authy.api import AuthyApiClient
import phonenumbers
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser


authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class PhoneSerializer(Serializer):  # noqa
    authy_phone = PhoneNumberField(required=True)

    def validate(self, data):
        phone = phonenumbers.parse(str(data.get("authy_phone")), None)
        authy_phone = authy_api.phones.verification_start(
            phone.national_number, phone.country_code
        )
        if authy_phone.ok():
            return data
        else:
            raise ValidationError(authy_phone.errors())


class PhoneTokenSerializer(Serializer):  # noqa
    authy_phone = PhoneNumberField(required=True)
    token = CharField(min_length=4, required=True, write_only=True)

    def validate(self, data):
        # test received phone 4 digit verification token from Twilio API
        phone = phonenumbers.parse(str(data.get("authy_phone")), None)
        authy_phone = authy_api.phones.verification_check(
            phone.national_number, phone.country_code, data.get("token")
        )
        if authy_phone.ok():
            return data
        else:
            raise ValidationError(authy_phone.errors())


class UserTokenSerializer(TokenObtainPairSerializer):  # noqa
    token = CharField(min_length=7, required=True)
