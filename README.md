# service_load_data_elasticsearch

service for loading json data into elasticsearch server

# Elastic Search Loading Data Service for Cloud Run

Elastic Search Service for loading data application for [Google Cloud Run][cloud_run].

[Cloud Run][cloud_run_docs] runs stateless [containers][cloud_container] on a fully managed environment or in your own GKE cluster.

[![Open in Cloud Shell][shell_img]][shell_link]

## Build

```
docker build --tag service-load-data-elasticsearch:latest .
```

## Test

```
docker-compose up test
```

## Deploy

```sh
# Set an environment variable with your GCP Project ID
export GOOGLE_CLOUD_PROJECT=<PROJECT_ID>

# Submit a build using Google Cloud Build
gcloud builds submit --tag gcr.io/${GOOGLE_CLOUD_PROJECT}/service-load-data-elasticsearch

# Deploy to Cloud Run
gcloud run deploy service-load-data-elasticsearch \
--image gcr.io/${GOOGLE_CLOUD_PROJECT}/service-load-data-elasticsearch
```

# Usage

This shows how to execute loaddata elasticsearch service locally.

## Run Locally

```
docker-compose up dev
```

You can configure your local elastcisearch adding a depend on the docker-compose.yaml file, using the `es` rule.

There is also fixtures to load Elastic Search Structures into a local database (sqlite db)

# Available routes to elastic

## Delete Elastic Search Index (Detection)

Endpoint that deletes Elastic Search Structure of Detection Index.

```sh
curl http://localhost:8080/detection/delete
```

## Create Elastic Search Index (Detection)

Endpoint that creates Detection Index Structure into Elastic Search server

```sh
curl http://localhost:8080/detection/create
```

It has its own structure, define on a local database. It follows the following structure:

```
{
  "mappings": {
    "properties": {
      "property_1": {
        "type": "keyword"
      },

      ...

      "property_n": {
        "type": "long"
      }
    }
  }
}
```

For tips on creating your own, take a look at [this link][mapping_url]

## Uploads Elastic Search Data (Detection)

Endpoint that inserts data into Detection Index, inside Elastic Search Server.

```sh
curl http://localhost:8080/detection/upload
```

It expects a geojson file, sent on a `file` field. It should have a [geojson structure][geojson_link] like this one:

```
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "stroke": "#555555",
        "stroke-width": 2,
        "stroke-opacity": 1,
        "fill": "#555555",
        "fill-opacity": 0.5
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -47.823486328125,
              -8.537565350804018
            ],
            [
              -47.109375,
              -8.537565350804018
            ],
            [
              -47.109375,
              -8.102738577783168
            ],
            [
              -47.823486328125,
              -8.102738577783168
            ],
            [
              -47.823486328125,
              -8.537565350804018
            ]
          ]
        ]
      }
    },

    ...

    {
      "type": "Feature",
      "properties": {
        "stroke": "#555555",
        "stroke-width": 2,
        "stroke-opacity": 1,
        "fill": "#555555",
        "fill-opacity": 0.5,
        "property": "value"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -48.251953125,
              -11.81358806977126
            ],
            [
              -48.636474609375,
              -13.12227980155627
            ],
            [
              -47.713623046875,
              -11.856599189585982
            ],
            [
              -48.251953125,
              -11.81358806977126
            ]
          ]
        ]
      }
    }
  ]
}
```

It gets geojson file, creates a [bulk file][bulk_file] from it and uses [Pandas][pandas_link] to serialize the data list so it can send smoothly to the Elastic Search Server.

It uses BasicElasticSearchStructure model for controlling how much, where and how to create the Index Structure inside Elastic Search.

# Future Plans

Currently, it only has one Index created (Detection). It would be nice to have more indexes inside the Elastic Search Server.

For new indexes, it needs a new BasicElasticSearchStructure, with new index name, url, structure and bulk_size_request, as well as new routes (create, update and delete) for the new index and tests.

[cloud_run]: https://cloud.run
[cloud_run_docs]: https://cloud.google.com/run/docs/
[cloud_container]: https://cloud.google.com/containers/
[shell_img]: http://gstatic.com/cloudssh/images/open-btn.png
[shell_link]: https://console.cloud.google.com/run/detail/us-central1/service-load-data-elasticsearch/metrics?project=custom-plating-209314&cloudshell=true
[mapping_url]: https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-put-mapping.html#put-mapping-api-multi-ex
[bulk_file]: https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html
[pandas_link]: https://pandas.pydata.org/docs/
[geojson_link]: https://geojson.org/
