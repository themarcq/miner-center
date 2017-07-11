from rest_framework import routers
from .views import WorkerStatViewSet, WorkerErrorViewSet
from django.conf.urls import url, include


router = routers.DefaultRouter()
router.register(r'stats', WorkerStatViewSet)
router.register(r'errors', WorkerErrorViewSet)


urlpatterns = [
    url(r'^', include(router.urls))
]
