from rest_framework import generics

from .models import Detection
from .serializers import DetectionSerializer

# Create your views here.


class UpdateJsonFileView(generics.CreateAPIView):
    serializer_class = DetectionSerializer
    queryset = Detection.objects.all()
