from rest_framework import generics, response, status

from .serializers import DetectionSerializer
from django.core.serializers import serialize, json
from .models import Detection, BasicElasticStructure

import pandas as pd
import json
import requests
import math

from datetime import datetime

now = datetime.now()


class UpdateDetectionView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        es_structure = BasicElasticStructure.objects.get(
            identifier='detection')
        print(f'[{datetime.now() - now}] starting process: ')

        detection_series = UtilFunctions.serialize_detection_file(request)

        ClearDetectionStructure.delete(request)

        CreateDetectionStructure.put(request)

        insert_errors = UtilFunctions.send_bulk_list(
            detection_series, es_structure)

        if (insert_errors):
            return response.Response({'msg': 'Some data were not inserted', 'errors': insert_errors}, status=status.HTTP_400_BAD_REQUEST)

        return response.Response({'msg': "Created"}, status=status.HTTP_201_CREATED)


class ClearDetectionStructure(generics.DestroyAPIView):
    def delete(request, *args, **kwargs):
        print(f'[{datetime.now() - now}] Clearing structure...')
        es_structure = BasicElasticStructure.objects.get(
            identifier='detection')

        UtilFunctions.delete_es_structure(es_structure)

        print(f'[{datetime.now() - now}] Clear!')

        return response.Response("Index removed", status=status.HTTP_200_OK)


class CreateDetectionStructure(generics.UpdateAPIView):
    def put(request, *args, **kwargs):
        print(f'[{datetime.now() - now}] Creating structure...')
        es_structure = BasicElasticStructure.objects.get(
            identifier='detection')

        UtilFunctions.create_es_structure(es_structure)

        print(f'[{datetime.now() - now}] Created!')

        return response.Response("Structure created", status=status.HTTP_200_OK)


class UtilFunctions:
    def create_es_structure(es_structure):
        req = requests.put(
            f'{es_structure.url}/{es_structure.identifier}',
            headers={"content-type": "application/json"},
            json=json.loads(es_structure.structure)
        )

        if req.status_code != 200 and req.status_code != 404:
            raise ValueError(f'Elastic Search clearing procedure \
                    returned error. Status code: {req.status_code} ${req.text}')

    def delete_es_structure(es_structure):
        req = requests.delete(
            f'{es_structure.url}/{es_structure.identifier}',
        )

        if req.status_code != 200 and req.status_code != 404:
            raise ValueError(f'Elastic Search clearing procedure \
                    returned error. Status code: {req.status_code} ${req.text}')

    def serialize_detection_file(request):
        print(f'[{datetime.now() - now}] serializing....')

        json_file = json.loads(request.FILES['file'].read())
        serializer = DetectionSerializer(data=json_file['features'], many=True)
        serializer.is_valid(raise_exception=True)

        print(f'[{datetime.now() - now}] Serialized!')

        return UtilFunctions.create_detection_series(
            serializer.validated_data)

    def create_detection_series(data):
        print(f'[{datetime.now() - now}] creating series....')

        pd_detections = pd.Series(
            [Detection(**value) for value in data])

        print(f'[{datetime.now() - now}] series created!')
        return pd_detections

    def send_bulk_list(bulk_list, es_structure):
        print(
            f'[{datetime.now() - now}] preparing bulk list of size {bulk_list.size}....')

        bulk_size = int(es_structure.bulk_size_request) or 1
        insert_errors = []
        chunks = math.ceil(bulk_list.size / bulk_size)

        for chunk_id in list(range(chunks)):
            lower_limiter = (chunk_id) * bulk_size
            higher_limiter = (chunk_id + 1) * bulk_size

            if higher_limiter >= len(bulk_list):
                higher_limiter = len(bulk_list)

            print(
                f'[{datetime.now() - now}] sending chunk {chunk_id + 1} ({lower_limiter + 1} to {higher_limiter} elements)....')

            body = [t.get_es_insertion_line()
                    for t in bulk_list[lower_limiter:higher_limiter]]

            req = requests.post(
                f'{es_structure.url}/{es_structure.identifier}/_bulk',
                headers={"content-type": "application/json"},
                data="".join(body)
            )

            if req.status_code != 200:
                raise ValueError(
                    f'Elastic Search returned error inserting data. Status code: {req.status_code} ${req.text}')

            if req.json()['errors']:
                insert_errors.extend([{'error': i['create']['error']['reason'], 'caused': i['create']
                                       ['error']['caused_by']} for i in req.json()['items'] if i['create']['status'] == 400])

        print(f'[{datetime.now() - now}] Sent')

        return insert_errors
