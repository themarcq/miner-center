from django.contrib import admin
from .models import Farm, Worker, GPUStat, WorkerStat, WorkerError


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    pass


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    pass


@admin.register(GPUStat)
class GPUStatAdmin(admin.ModelAdmin):
    pass


@admin.register(WorkerStat)
class WorkerStatAdmin(admin.ModelAdmin):
    readonly_fields=('timestamp',)


@admin.register(WorkerError)
class WorkerErrorAdmin(admin.ModelAdmin):
    pass

