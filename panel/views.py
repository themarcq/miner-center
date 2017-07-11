from django import views
from farms.models import Farm
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin


class PanelView(LoginRequiredMixin, views.View):
    def get(self, request):
        return render(request, 'panel/panel.html', {
            'farms': Farm.objects.all()
        })
