from rest_framework import viewsets
from .models import WorkerStat, WorkerError
from .serializers import WorkerStatSerializer, WorkerErrorSerializer


class WorkerStatViewSet(viewsets.ModelViewSet):
    queryset = WorkerStat.objects.all()
    serializer_class = WorkerStatSerializer


class WorkerErrorViewSet(viewsets.ModelViewSet):
    queryset = WorkerError.objects.all()
    serializer_class = WorkerErrorSerializer
