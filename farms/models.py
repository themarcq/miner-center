from django.db import models
from datetime import datetime, timedelta, date
from django.utils import timezone
import json
from math import ceil, floor
from .utils import exception_handle


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

    resolution = 100 # number of points to generate to show

    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self._stats = None
        self._timedelta = timedelta(hours=8)
        self.gpu_number = 0

    def set_data_length(self,length):
        self._stats = None
        self.gpu_number = 0
        if length == '24hours':
            self._timedelta = timedelta(days=1)
        elif length == 'week':
            self._timedelta = timedelta(days=7)
        elif length == 'month':
            self._timedelta = timedelta(days=30)
        elif length == '8hours':
            self._timedelta = timedelta(hours=8)
        else:
            raise ValueError

    @property
    def newest_stat(self):
        return self.stats.filter(timestamp__gte=timezone.now()-timedelta(minutes=2)).order_by('timestamp').last()

    @property
    def stats_data(self):
        if not self._stats:
            # get data from database and fill the gaps with zeros
            since_date = timezone.now()-self._timedelta
            stats = self.stats.filter(timestamp__gte=since_date)\
                .order_by('timestamp')
            stats_fixed = []
            for stat in stats:
                self.gpu_number = max(self.gpu_number, len(stat.gpu_stats.all()))
                if len(stats_fixed) == 0:
                    if (stat.timestamp - (since_date)).total_seconds()/60 > 2:
                        stats_fixed.append({
                            'timestamp': since_date.timestamp()*1000,
                            'total_hashrate': 0,
                            'gpu_stats': []
                        })
                    else:
                        stats_fixed.append({
                            'timestamp': stat.timestamp.timestamp()*1000,
                            'total_hashrate': stat.total_hashrate/1000.,
                            'gpu_stats': [{
                                'hashrate': gpu.hashrate/1000.,
                                'temperature': gpu.temperature,
                                'fan_speed': gpu.fan_speed
                            } for gpu in stat.gpu_stats.all()]
                        })
                        continue
                for time in range(int(stats_fixed[-1]['timestamp']+60000), int(stat.timestamp.timestamp()*1000-60000), 60000):
                    stats_fixed.append({
                        'timestamp': time,
                        'total_hashrate': 0,
                        'gpu_stats': []
                    })
                stats_fixed.append({
                    'timestamp': stat.timestamp.timestamp()*1000,
                    'total_hashrate': stat.total_hashrate/1000.,
                    'gpu_stats': [{
                        'hashrate': gpu.hashrate/1000.,
                        'temperature': gpu.temperature,
                        'fan_speed': gpu.fan_speed
                    } for gpu in stat.gpu_stats.all()]
                })
            del stats
            # fill out missing graphic cards
            for stat in stats_fixed:
                stat['gpu_stats'] += [{
                    'hashrate': 0,
                    'temperature': 0,
                    'fan_speed': 0
                }for i in range(self.gpu_number - len(stat['gpu_stats']))]

            # compress it to set resolution
            if len(stats_fixed) < self.resolution:
                self._stats = stats_fixed
            else:
                compressed_stats = []
                ratio = self.resolution/float(len(stats_fixed))
                for i in range(1,self.resolution+1):
                    first = int(ceil((i-1)/ratio))
                    last = int(ceil((i)/ratio))
                    cut = stats_fixed[first:last]
                    cut_length = float(last-first)
                    compressed_stats.append({
                        'timestamp': (since_date + ((timezone.now()-since_date)/self.resolution*i)).timestamp()*1000,
                        'total_hashrate': sum([o['total_hashrate'] for o in cut])/cut_length,
                        'gpu_stats': [{
                            'hashrate': sum([o['gpu_stats'][j]['hashrate'] for o in cut])/cut_length,
                            'temperature': sum([o['gpu_stats'][j]['temperature'] for o in cut])/cut_length,
                            'fan_speed': sum([o['gpu_stats'][j]['fan_speed'] for o in cut])/cut_length
                        } for j in range(self.gpu_number)]
                    })
                self._stats = compressed_stats
        return self._stats

    @property
    @exception_handle
    def total_hashrate_data(self):
        return json.dumps([['Time', 'Hashrate']]+[
            [stat['timestamp'], stat['total_hashrate']] for stat in self.stats_data
        ])

    def get_gpu_stat(self, attr):
        stats_data = self.stats_data
        data = [['Time']+["Card #{}".format(i) for i in range(self.gpu_number)]]
        for stat in stats_data:
            datum = [stat['timestamp']] + [gpu[attr] for gpu in stat['gpu_stats']]
            data.append(datum)
        return json.dumps(data)

    @property
    @exception_handle
    def temperatures_data(self):
        return self.get_gpu_stat('temperature')

    @property
    @exception_handle
    def hashrates_data(self):
        return self.get_gpu_stat('hashrate')


    @property
    @exception_handle
    def fan_speeds_data(self):
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
