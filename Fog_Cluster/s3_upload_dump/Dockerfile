FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

COPY ./cluster_config.json /config/cluster_config.json

COPY ./s3_key.json /config/s3_key.json


WORKDIR /app

RUN pip3 install --default-timeout=100 -r requirements.txt

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]

