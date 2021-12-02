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
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)

        # import pdb
        # pdb.set_trace()

        # serializer.save()

        bulk_list = self.create_bulk_es(serializer.validated_data)

        self.send_bulk_list(bulk_list)

        return response.Response("{msg: OK}", status=status.HTTP_201_CREATED)

    def create_bulk_es(self, data):
        detections = [Detection(**value) for value in data]

        return [detec.get_es_insertion_line() for detec in detections]

    def send_bulk_list(self, bulk_list):
        print(bulk_list)
