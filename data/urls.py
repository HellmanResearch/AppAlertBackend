from rest_framework import routers

from . import views as l_views


router = routers.DefaultRouter(trailing_slash=False)

# router.register("accounts", viewset=l_views.Account)
# router.register("operators", viewset=l_views.Operator)
# router.register("performances", viewset=l_views.Performance)


urlpatterns = router.urls
