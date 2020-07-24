FROM ubuntu:18.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --default-timeout=100 -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]

