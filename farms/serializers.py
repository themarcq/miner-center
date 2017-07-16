from rest_framework import serializers
from .models import Worker, WorkerStat, WorkerError, GPUStat


class GPUStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPUStat
        exclude = ('stat',)


class WorkerStatSerializer(serializers.ModelSerializer):
    gpu_stats = GPUStatSerializer(many=True)
    worker_id = serializers.IntegerField()

    class Meta:
        model = WorkerStat
        exclude = ('timestamp', "worker")

    def create(self, validated_data):
        gpu_stats = validated_data.pop('gpu_stats', [])
        worker_id = validated_data.pop('worker_id', None)
        worker,_ = Worker.objects.get_or_create(
            farm=self.context['request'].user.farm,
            index=int(worker_id),
            defaults={'label': 'Unknown'}
        )
        stat = WorkerStat.objects.create(worker=worker, **validated_data)
        self._create_gpu_Stats(stat, gpu_stats)
        return stat

    def _create_gpu_Stats(self, instance, gpu_stats):
        GPUStat.objects.filter(stat=instance).delete()
        for gpu in gpu_stats:
            GPUStat.objects.create(stat=instance, **gpu)


class WorkerErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerError
        exclude = ('timestamp',)
