from django import views
from farms.models import Farm
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin


class PanelView(LoginRequiredMixin, views.View):
    def get(self, request, length="8hours"):
        farms_query = Farm.objects.all().prefetch_related('workers').prefetch_related('workers__stats').prefetch_related('workers__stats__gpu_stats')
        farms = [
            {
                'label': farm.label,
                'workers': list(farm.workers.all())
            } for farm in farms_query
        ]
        for farm in farms:
            for worker in farm['workers']:
                worker.set_data_length(length)

        #DEBUG
#        for farm in farms:
#            for worker in farm['workers']:
#                worker.fan_speeds_data
        #DEBUG

        return render(request, 'panel/panel.html', {
            'farms': farms
        })
