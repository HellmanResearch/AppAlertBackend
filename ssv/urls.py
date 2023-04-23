from rest_framework import routers

from . import views as l_views


router = routers.DefaultRouter(trailing_slash=False)

router.register("operators", viewset=l_views.Operator)
router.register("validators", viewset=l_views.Validator)
router.register("clusters", viewset=l_views.Cluster)
# router.register("performances", viewset=l_views.Performance)


urlpatterns = router.urls
