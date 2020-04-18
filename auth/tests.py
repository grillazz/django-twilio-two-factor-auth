from unittest.mock import patch, MagicMock

from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_206_PARTIAL_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)
from authy.api.resources import User

from rest_framework.test import APITestCase
from .models import CustomUser


class BaseTestCase(APITestCase):
    def setUp(self):
        self.username = "mc_hammer"
        self.password = "can_touch_this"
        self.user = CustomUser.objects.create(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        # authy api mocks goes here
        mock_response = MagicMock()
        mock_resource = MagicMock()
        self.mock_user = MagicMock(User(mock_resource, mock_response))
        self.mock_user.content = {
            "user": {"id": 98765432},
            "success": True,
            "message": "Message from authy api.",
        }
        self.mock_user.errors = MagicMock(return_value={})
        self.mock_user.ok = MagicMock(return_value=True)
        self.mock_user.id = 98765432


class AuthenticationApiTest(BaseTestCase):
    def obtain_jwt(self):
        payload = {"username": self.username, "password": self.password}
        response = self.client.post(
            reverse("token_obtain_pair"), payload, format="json"
        )

        return response

    def test_obtain_jwt(self):
        # # obtain jwt
        jwt_response = self.obtain_jwt()
        self.assertEqual(jwt_response.status_code, HTTP_200_OK)
        self.assertTrue("refresh" in jwt_response.data)
        self.assertTrue("access" in jwt_response.data)
        self.client.logout()
        # try to login with incorrect jwt
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer {}".format("stuff and nonsense")
        )
        get_user_response = self.client.get(
            reverse("custom_auth:customuser-list"), data={"format": "json"}
        )
        self.assertEqual(get_user_response.status_code, HTTP_401_UNAUTHORIZED)
        # login with jwt
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer {}".format(jwt_response.data["access"])
        )
        get_user_response = self.client.get(
            reverse("custom_auth:customuser-list"), data={"format": "json"}
        )
        self.assertEqual(get_user_response.status_code, HTTP_200_OK)

    @patch("auth.serializers.authy_api", autospec=True)
    def test_verify_phone_number_for_user(self, mock_authy_api):
        jwt_response = self.obtain_jwt()

        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer {}".format(jwt_response.data["access"])
        )

        payload = {"authy_phone": "+48123456789"}
        response = self.client.post(reverse("2fa_phone_verify"), payload, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    @patch("auth.views.authy_api", autospec=True)
    @patch("auth.serializers.authy_api", autospec=True)
    def test_register_phone_number_for_user(
        self, mock_authy_api_serializers, mock_authy_api_views
    ):
        jwt_response = self.obtain_jwt()

        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer {}".format(jwt_response.data["access"])
        )
        # mock twilio api response
        mock_authy_api_views.users.create = MagicMock(return_value=self.mock_user)
        # register phone for two factor autentication
        payload = {"authy_phone": "+48123456789", "token": 1234}
        response = self.client.post(
            reverse("2fa_register_phone"), payload, format="json"
        )
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    @patch("auth.views.authy_api", autospec=True)
    @patch("auth.serializers.authy_api", autospec=True)
    def test_obtain_jwt_with_twofa(
        self, mock_authy_api_serializers, mock_authy_api_views
    ):
        jwt_response = self.obtain_jwt()

        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer {}".format(jwt_response.data["access"])
        )
        # mock twilio api response
        mock_authy_api_views.users.create = MagicMock(return_value=self.mock_user)
        # register phone with twilio api
        payload = {"authy_phone": "+48123456789", "token": 1234}
        self.client.post(reverse("2fa_register_phone"), payload, format="json")
        jwt_response = self.obtain_jwt()
        self.assertEqual(jwt_response.status_code, HTTP_206_PARTIAL_CONTENT)
        self.assertEqual(
            jwt_response.json(),
            {"message": "SMS request successful. 2FA token verification expected."},
        )
        # obtain jwt with correct two factor authentication token
        payload = {
            "username": self.username,
            "password": self.password,
            "token": 12345678,
        }
        token_response = self.client.post(
            reverse("2fa_token_verify"), payload, format="json"
        )
        self.assertEqual(token_response.status_code, HTTP_200_OK)
        self.assertTrue("refresh" in token_response.data)
        self.assertTrue("access" in token_response.data)
        # obtain jwt with incorrect two factor token
        payload = {
            "username": self.username,
            "password": self.password,
            "token": "wrong1",
        }
        token_response = self.client.post(
            reverse("2fa_token_verify"), payload, format="json"
        )
        self.assertEqual(
            token_response.json(),
            {"token": ["Ensure this field has at least 7 characters."]},
        )
        self.assertEqual(token_response.status_code, HTTP_400_BAD_REQUEST)
        # obtain jwt with two factor token for not registered user
        payload = {
            "username": "wrong_username",
            "password": "some_password",
            "token": 12345678,
        }
        token_response = self.client.post(
            reverse("2fa_token_verify"), payload, format="json"
        )
        self.assertEqual(
            token_response.json(),
            {"detail": "No active account found with the given credentials"},
        )
        self.assertEqual(token_response.status_code, HTTP_401_UNAUTHORIZED)
