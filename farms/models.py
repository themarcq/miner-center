from django.db import models
from datetime import datetime, timedelta
import json
import logging
from functools import wraps
from datetime import timedelta, date


def timerange(start_date, end_date):
    for n in range(int ((end_date - start_date).seconds//60-1)):
        yield start_date + timedelta(minutes=n+1)


class DummyWorkerStat():
    def __init__(self, time):
        self.timestamp = time
        self.update = 0
        self.total_hashrate = 0
        self.shares = 0
        self.rejected_shares = 0
        self.gpu_stats = []


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

    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self._last_week_stats = None
        self._gpu_data = None

    @property
    def newest_stat(self):
        return self.stats.filter(timestamp__gte=datetime.now()-timedelta(minutes=2)).order_by('timestamp').last()

    @property
    def last_week_stats(self):
        if not self._last_week_stats:
            stats = self.stats.filter(timestamp__gte=datetime.now()-timedelta(hours=8))\
                .order_by('timestamp')\
                .prefetch_related('gpu_stats')
            stats_fixed = []
            for stat in stats:
                if len(stats_fixed) == 0:
                    stats_fixed.append(stat)
                    continue
                for time in timerange(stats_fixed[-1].timestamp, stat.timestamp):
                    stats_fixed.append(DummyWorkerStat(time))
                stats_fixed.append(stat)
            self._last_week_stats = stats_fixed
        return self._last_week_stats

    @property
    @exception_handle
    def last_week_total_hashrate_data(self):
        return json.dumps([['Time', 'Hashrate']]+[
            [stat.timestamp.timestamp()*1000, stat.total_hashrate/1000.] for stat in self.last_week_stats
        ])

    def gpu_data(self, stats):
        if self._gpu_data is None:
            cards_number = 0
            for stat in stats:
                cards_number = max(cards_number, len(stat.gpu_stats.all()) if stat.gpu_stats else 0)
            title = ['Time'] + ['Card #{}'.format(i) for i in range(cards_number)]
            data = [title]
            for stat in stats:
                datum = [stat.timestamp.timestamp()*1000]
                for card in range(cards_number):
                    try:
                        if stat.gpu_stats:
                            gpu = stat.gpu_stats.all()[card]
                        else:
                            raise IndexError
                    except IndexError:
                        datum.append(None)
                    else:
                        datum.append(gpu)
                data.append(datum)
            self._gpu_data = data
        return self._gpu_data

    def get_gpu_stat(self, attr):
        gpu_data = self.gpu_data(self.last_week_stats)
        data = [gpu_data[0]]
        for gpu_stat_list in gpu_data[1:]:
            datum = [gpu_stat_list[0]]
            for gpu_stat in gpu_stat_list[1:]:
                if gpu_stat:
                    datum.append(getattr(gpu_stat, attr, 0))
                else:
                    datum.append(0)
            data.append(datum)
        return json.dumps(data)

    @property
    @exception_handle
    def last_week_temperatures_data(self):
        return self.get_gpu_stat('temperature')

    @property
    @exception_handle
    def last_week_hashrates_data(self):
        return self.get_gpu_stat('hashrate')


    @property
    @exception_handle
    def last_week_fan_speeds_data(self):
        return self.get_gpu_stat('fan_speed')


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
