from django.apps import AppConfig


class FarmsConfig(AppConfig):
    name = 'farms'

    def ready(self):
        from  . import signals
