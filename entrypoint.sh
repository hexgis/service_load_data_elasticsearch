#!/bin/bash
set -e

if [ ! -z "${GOOGLE_APPLICATION_CREDENTIALS}" ]
then
  if [ ! -z "${GOOGLE_APPLICATION_CREDENTIALS_JSON}" ]
  then
    mkdir -p $(dirname "${GOOGLE_APPLICATION_CREDENTIALS}")
    echo "${GOOGLE_APPLICATION_CREDENTIALS_JSON}" > "${GOOGLE_APPLICATION_CREDENTIALS}"
  else
    echo "No Google Cloud Application Credentials provided"
    exit 0
  fi
fi

gcloud auth activate-service-account --key-file ${GOOGLE_APPLICATION_CREDENTIALS}

exec "$@"
