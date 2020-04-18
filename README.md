## About

 In these days we need to be sure that data which we using and sharing is consistent and we can trust in it.
One of methods is protect your api as best as possibile.
I decided to share my approach to protect Django REST Framework JWT with Twilio 2FA.
Hope it will save time which i spent to implement Twilio 2FA for REST API safely.
In this sample project i showing integration with Verify API and Authy API from Twilio for Python.

My assumption here is that you have exp with Django and DRF.
If you don't please visit first:
https://www.djangoproject.com/ and https://www.django-rest-framework.org/
You can also write some good book i.e. https://wsvincent.com/best-django-books/

## Local development

Now what you need to start:

1. create Twilio account and add Authy App in Twilio console. Instructions you can find here:...

2. clone this project and in setting.py replace ACCOUNT_SECURITY_API_KEY value with your new key

3. next you will python manege.py migrations and python manege.py createsuperuser

## How it works

cURL examples in progress...

## ToDo

- [x] Uni tests 80% coverage
- [ ] Update Readme File
- [x] Postman test collection
- [ ] cURL examples

## License

[MIT](http://www.opensource.org/licenses/mit-license.html)

## Disclaimer

No warranty expressed or implied. Software is as is.