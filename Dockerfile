# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-buster

LABEL maintainer="Hexgis <contato@hexgis.com>"

ENV APP_HOME /app
ENV PORT 8080
WORKDIR $APP_HOME

# Removes output stream buffering, allowing for more efficient logging
ENV PYTHONUNBUFFERED 1
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add -

# Install system requirements
RUN apt-get update -y
RUN apt-get install -y \
    build-essential \
    libgnutls28-dev \
    python3-setuptools \
    python3-pip \
    python-dev \
    python-pil \
    python-gdal \
    libgdal-dev \
    gdal-bin \
    dans-gdal-scripts \
    google-cloud-sdk \
    && rm -rf /var/lib/apt/lists/*
RUN pip uninstall gdal -y
RUN pip install numpy
RUN pip install gdal==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
COPY . .

# Entrypoint configuration
# COPY ./entrypoint.sh /scripts/entrypoint.sh
# RUN chmod +x /scripts/entrypoint.sh
# ENTRYPOINT [ "/scripts/entrypoint.sh" ]

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD python manage.py runserver 0.0.0.0:$PORT
