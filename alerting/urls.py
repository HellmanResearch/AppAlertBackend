from rest_framework import routers

from . import views as l_views


router = routers.DefaultRouter(trailing_slash=False)

router.register("test-task", viewset=l_views.TestTask, basename="test-task")
router.register("alerts", viewset=l_views.Alert)
router.register("subscribes", viewset=l_views.Subscribe)


urlpatterns = router.urls
