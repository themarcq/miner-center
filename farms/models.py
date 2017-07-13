from django.db import models
from datetime import datetime, timedelta
import json
import logging
from functools import wraps


logger = logging.getLogger('miner_center')


def exception_handle(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        def try_except(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.debug(e)
                raise
        return try_except(*args, **kwargs)
    return wrapper


class Farm(models.Model):
    user = models.OneToOneField(
        'auth.User',
        verbose_name="User",
        on_delete=models.CASCADE)

    label = models.CharField(
        verbose_name="Label",
        max_length=1024)


class Worker(models.Model):
    farm = models.ForeignKey(
        'farms.Farm',
        verbose_name='Farm',
        on_delete=models.CASCADE,
        related_name='workers')

    label = models.CharField(
        max_length=1024)

    description = models.TextField(
        null=True, blank=True)

    index = models.PositiveIntegerField()

    @property
    def newest_stat(self):
        return self.stats.order_by('timestamp').last()

    @property
    def last_week_stats(self):
        return self.stats.filter(timestamp__gte=datetime.now()-timedelta(days=7))\
                .prefetch_related('gpu_stats')

    @property
    @exception_handle
    def last_week_total_hashrate_data(self):
        return json.dumps([o.total_hashrate for o in self.last_week_stats])


class WorkerStat(models.Model):
    worker = models.ForeignKey(
        'farms.Worker',
        on_delete=models.CASCADE,
        related_name='stats')

    timestamp = models.DateTimeField(
            auto_now_add=True)

    uptime = models.PositiveIntegerField()
    total_hashrate = models.PositiveIntegerField()
    shares = models.PositiveIntegerField()
    rejected_shares = models.PositiveIntegerField()


class GPUStat(models.Model):
    stat = models.ForeignKey(
        'farms.WorkerStat',
        on_delete=models.CASCADE,
        related_name='gpu_stats')

    hashrate = models.PositiveIntegerField()
    temperature = models.PositiveIntegerField()
    fan_speed = models.PositiveIntegerField()


class WorkerError(models.Model):
    worker = models.ForeignKey(
        'farms.Worker',
        on_delete=models.CASCADE,
        related_name='errors')

    timestamp = models.DateTimeField(
            auto_now_add=True)

    error = models.TextField()
