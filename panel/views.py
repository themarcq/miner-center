from django import views
from farms.models import Farm
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class PanelView(LoginRequiredMixin, views.View):
    def get(self, request, length="8hours"):
        farms_query = Farm.objects.all().prefetch_related('workers')

        farms = [
            {
                'label': farm.label,
                'workers': list(farm.workers.all())
            } for farm in farms_query
        ]

        for farm in farms:
            for worker in farm['workers']:
                worker.set_data_length(length)

        return render(request, 'panel/panel.html', {
            'farms': farms,
            'client_ip': get_client_ip(request)
        })
