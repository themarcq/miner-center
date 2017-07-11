from django.conf.urls import url
from .views import PanelView
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^$', PanelView.as_view(), name='panel'),
    url(r'^login/$', auth_views.LoginView.as_view()),
]
