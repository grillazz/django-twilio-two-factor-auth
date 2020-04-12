from rest_framework import routers

from .views import CustomUserViewSet

router = routers.SimpleRouter()
router.register(r"users", CustomUserViewSet)
urlpatterns_auth = router.urls
