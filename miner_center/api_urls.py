from farms import api_urls as farms_api_urls
from django.conf.urls import url, include


urlpatterns = [
    url(r'^farms/', include(farms_api_urls)),
]
