
from rest_framework import routers

from . import views as l_views


router = routers.DefaultRouter(trailing_slash=False)


router.register("users", viewset=l_views.User)


urlpatterns = router.urls
