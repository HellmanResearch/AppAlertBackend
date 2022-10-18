
from rest_framework import routers

from . import views as l_views


router = routers.DefaultRouter(trailing_slash=False)


# router.register("alerts", viewset=l_views.Alert)
router.register("metric-groups", viewset=l_views.MetricGroup)
router.register("metrics", viewset=l_views.Metric)
router.register("alerts", viewset=l_views.Alert)


urlpatterns = router.urls
