from rest_framework import routers

from . import views as l_views


router = routers.DefaultRouter(trailing_slash=False)

router.register("alerts", viewset=l_views.Alert)
router.register("subscribes", viewset=l_views.Subscribe)


urlpatterns = router.urls
