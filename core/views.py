from rest_framework import generics, serializers, parsers, response, status

from .serializers import DetectionSerializer, UploadSerializer
from django.core.serializers import serialize, json
from .models import Detection, BasicElasticStructure

import pandas as pd
import json
import requests
import math

from datetime import datetime


class UpdateDetectionView(generics.CreateAPIView):
    queryset = Detection.objects.all()
    serializer_class = DetectionSerializer

    def post(self, request, *args, **kwargs):

        es_structure = BasicElasticStructure.objects.get(
            identifier='detection')
        self.now = datetime.now()
        print(f'[{datetime.now() - self.now}] starting process: ')
        print(f'[{datetime.now() - self.now}] serializing....')

        json_file = json.loads(request.FILES['file'].read())
        serializer = DetectionSerializer(data=json_file['features'], many=True)
        serializer.is_valid(raise_exception=True)

        # import pdb
        # pdb.set_trace()

        print(f'[{datetime.now() - self.now}] Serialized!')

        bulk_list = self.create_bulk_es(serializer.validated_data)

        self.send_bulk_list(bulk_list, es_structure)

        return response.Response("{msg: OK}", status=status.HTTP_201_CREATED)

    def create_bulk_es(self, data):
        print(f'[{datetime.now() - self.now}] creating series....')
        # pd_bulk_list = [Detection(**value).get_es_insertion_line()
        #                 for value in data]

        pd_detections = pd.Series(
            [Detection(**value) for value in data])
        pd_bulk_list = pd_detections.apply(
            lambda x: x.get_es_insertion_line())

        # import pdb
        # pdb.set_trace()

        print(f'[{datetime.now() - self.now}] series created!')
        return pd_bulk_list

    def send_bulk_list(self, bulk_list, es_structure):
        print(f'[{datetime.now() - self.now}] preparing bulk list....')
        # print(bulk_list)

        bulk_size = int(es_structure.bulk_size_request) or 1

        import pdb
        pdb.set_trace()

        chunks = math.ceil(bulk_list.size / bulk_size)

        for chunk_id in list(range(chunks)):
            lower_limiter = (chunk_id) * bulk_size
            higher_limiter = (chunk_id + 1) * bulk_size

            if higher_limiter >= bulk_list.size:
                higher_limiter = bulk_list.size

            print(
                f'[{datetime.now() - self.now}] sending chunk {chunk_id + 1} ({lower_limiter + 1} to {higher_limiter} elements)....')

            # print(
            #     f'{bulk_list.iloc[lower_limiter:higher_limiter].to_string()} \n')

            requests.post(
                f'{es_structure.url}/{es_structure.es_identifier}/_bulk',
                headers={"content-type": "application/json"},
                data=f'{bulk_list.iloc[lower_limiter:higher_limiter].to_string()} \n'
            )

        print(f'[{datetime.now() - self.now}] Sent')


class ClearDetectionStructure(generics.DestroyAPIView):

    def delete(request, *args, **kwargs):
        es_structure = BasicElasticStructure.objects.get(
            identifier='detection')

        req = requests.delete(
            f'{es_structure.url}/{es_structure.identifier}',
        )

        if req.status_code != 200 and req.status_code != 404:
            raise ValueError(f'Elastic Search clearing procedure \
                    returned error. Status code: {req.status_code} ${req.text}')

        return True

        # print("TODO")


class CreateDetectionStructure(generics.UpdateAPIView):

    def put(request, *args, **kwargs):
        es_structure = BasicElasticStructure.objects.get(
            identifier='detection')

        req = requests.put(
            f'{es_structure.url}/{es_structure.identifier}',
            headers={"content-type": "application/json"},
            json=json.loads(es_structure.structure)
        )

        if req.status_code != 200 and req.status_code != 404:
            raise ValueError(f'Elastic Search clearing procedure \
                    returned error. Status code: {req.status_code} ${req.text}')

        return True

        # print("TODO")
