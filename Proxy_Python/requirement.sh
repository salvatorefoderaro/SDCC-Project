#!/bin/bash

sudo apt-get install -y python-pip python-dev
pip install --default-timeout=100 -r requirements.txt