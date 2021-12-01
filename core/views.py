from rest_framework import generics, serializers, parsers, response, status

from .models import Detection
from .serializers import DetectionSerializer, UploadSerializer
from django.core.serializers import serialize, json

import json


class UpdateJsonFileView(generics.CreateAPIView):
    queryset = Detection.objects.all()
    serializer_class = DetectionSerializer

    # def create(self, request, *args, **kwargs):
    #     jsonfile = json.loads(request.FILES['file'].read())
    #     serializer = DetectionSerializer(data=jsonfile['features'], many=True)
    #     serializer.is_valid()
    #     headers = self.get_success_headers(serializer.data)
    #     # self.perform_create(serializer)

    #     import pdb
    #     pdb.set_trace()

    #     return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def post(self, request, *args, **kwargs):

        json_file = json.loads(request.FILES['file'].read())
        serializer = DetectionSerializer(data=json_file['features'], many=True)
        if serializer.is_valid():
            self.create_es(serializer.data)

        return response.Response(ser.data, status=status.HTTP_201_CREATED)

    def create_es(self, data):
        import pdb
        pdb.set_trace()

        detection = Detection(**data)
