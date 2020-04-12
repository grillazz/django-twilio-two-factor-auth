from django.contrib.auth.models import AbstractUser
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField
import phonenumbers


class CustomUser(AbstractUser):
    authy_phone = PhoneNumberField(
        null=True,
        blank=True,
        unique=True,
        help_text="This phone number is dedicated to Twilio 2FA Authentication.",
    )
    authy_id = models.CharField(
        max_length=12,
        blank=True,
        help_text="Authentication ID received from Twilio 2FA Api.",
    )

    def get_authy_phone(self):
        try:
            parsed = phonenumbers.parse(str(self.authy_phone), None)
        except phonenumbers.NumberParseException:
            return None
        return parsed

    def is_twofa_on(self):
        if self.get_authy_phone() is not None and self.authy_id.isdigit():
            return True
        else:
            return False
