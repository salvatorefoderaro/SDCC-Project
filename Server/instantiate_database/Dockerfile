FROM ubuntu:18.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

COPY ./config.json /config/config.json

WORKDIR /app

RUN pip install --default-timeout=100 -r requirements.txt

COPY . /app

RUN rm config.json

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]

