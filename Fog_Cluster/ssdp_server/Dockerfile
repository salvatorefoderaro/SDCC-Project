FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

# We copy just the requirements.txt first to leverage Docker cache

WORKDIR /app

COPY . /app

RUN pip3 install --default-timeout=100 -r requirements.txt

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]

