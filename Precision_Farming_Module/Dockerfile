FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip3 install --default-timeout=100 -r requirements.txt

COPY . /app

EXPOSE 80

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]

