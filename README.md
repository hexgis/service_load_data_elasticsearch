# service_load_data_elasticsearch
service for loading json data into elasticsearch server

# Skyland Catalog Processor Service for Cloud Run

Skyland Catalog Processor Service application for [Google Cloud Run][cloud_run].

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

This examples shows how to execute loaddata elasticsearch service and available routes.

## Run Locally

```
docker-compose up dev
```

## Available routes to elastic

```sh
curl http://localhost:8080/detection/delete
curl http://localhost:8080/detection/upload
curl http://localhost:8080/detection/create
```

[cloud_run]: https://cloud.run
[cloud_run_docs]: https://cloud.google.com/run/docs/
[cloud_container]: https://cloud.google.com/containers/
[shell_img]: http://gstatic.com/cloudssh/images/open-btn.png
[shell_link]: https://console.cloud.google.com/run/detail/us-central1/service-load-data-elasticsearch/metrics?project=custom-plating-209314&cloudshell=true
