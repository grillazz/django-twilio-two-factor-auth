[![Build Status](https://travis-ci.com/grillazz/twofa_for_drf.svg?branch=master)](https://travis-ci.com/grillazz/twofa_for_drf)
[![Coverage Status](https://coveralls.io/repos/github/grillazz/twofa_for_drf/badge.svg?branch=master)](https://coveralls.io/github/grillazz/twofa_for_drf?branch=master)
## About

 In these days we need to be sure that data which we using and sharing is consistent and we can trust in it.
One of methods is protect your api as best as possibile.
I decided to share my approach to protect Django REST Framework JWT with Twilio 2FA.
Hope it will save time which i spent to implement Twilio 2FA for REST API safely.
In this sample project i showing integration with Authy API from Twilio for Python.

My assumption here is that you have exp with Django and DRF.
If you don't please visit first:
https://www.djangoproject.com/ and https://www.django-rest-framework.org/
You can also write some good book i.e. https://wsvincent.com/best-django-books/

## Local development

Now what you need to start:

1. Create Twilio account and add Authy App in Twilio console. You can find the instructions here: https://www.twilio.com/try-twilio

2. Clone this project and in setting.py replace ACCOUNT_SECURITY_API_KEY value with your new key.

3. Next you will python manege.py migrations and python manege.py createsuperuser

## How it works

#### Step 0: Django Rest Framework JWT Authentication when 2FA disabled:

for below cURL

```console
curl --location --request POST 'http://127.0.0.1:8000/api/token/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "twilio",
    "password": "twiliopass"
}'
```

we receive response with HTTP code 200 with JSON body
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU4ODQ5NjY0OSwianRpIjoiMDcwNTJhNjc3OWIwNDJiMGE3ZmNkYzkxMmNiNTJkMTYiLCJ1c2VyX2lkIjo0fQ.h3KeHB29WiMQgdpsdJbmNy6mATGzTL4_MBWmQf1jZDE",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTg4NDEwNTQ5LCJqdGkiOiI5NWVlOWUxNDU0MTk0MDc3ODlhMzQ3N2VkNGI0NDEwZSIsInVzZXJfaWQiOjR9.XJO7d9qH3F0nKp9AQg9AIaySKLqBKPVzG-yvkxLhwOs"
}
```

#### Step 1:  Phone verification view with TwilioAuthy API.

This endpoint will check if user mobile phone number is valid.
If YES Twilio API send 4 digit verification token via SMS.


```console
curl --location --request POST 'http://127.0.0.1:8000/api/2fa/phone-verify/' \
--header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTg4NDEwOTE1LCJqdGkiOiJkYjNhYTgwYjVmYTg0ZTk5YTAyMTI5YzU0MjBkZTJlOCIsInVzZXJfaWQiOjJ9.aY2UQiDMON3X2Ibvlj0KyocTmc5RS7jeLP9RjO58ynk' \
--header 'Content-Type: application/json' \
--data-raw '{
	"authy_phone": "+48123456789"
}'
```
we receive response with HTTP code 204 with no JSON body



cURL examples in progress...

## ToDo

- [x] Uni tests 80% coverage
- [x] Update Readme File
- [x] Postman test collection
- [ ] cURL examples

## License

[MIT](http://www.opensource.org/licenses/mit-license.html)

## Disclaimer

No warranty expressed or implied. Software is as is.