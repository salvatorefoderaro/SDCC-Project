FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
COPY ./config.json /config/config.json

WORKDIR /app

RUN pip3 install --default-timeout=100 -r requirements.txt

COPY . /app

RUN rm config.json

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]

