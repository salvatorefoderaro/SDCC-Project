#!/bin/bash

minikube start
minikube addons enable storage-provisioner
eval $(minikube docker-env)
cd check_devices_status && docker build -t checkdevicestatus:v1 .
cd ../collect_data && docker build -t collectdata:v1 .
cd ../instantiate_database && docker build -t dbinstantiate:v1 .
cd ../dashboard && docker build -t dashboard:v1 .
cd ../get_devices_stat && docker build -t getdevicesstat:v1 .
cd ../s3_upload_dump && docker build -t uploads3:v1 .
cd ../calculate_value && docker build -t calculatevalue:v1 .
cd ../yaml
docker pull mysql:latest
kubectl apply -f secret.yaml
sleep 4
kubectl apply -f mysql-dump.yaml
sleep 4
kubectl apply -f mysql-pv.yaml
sleep 4
kubectl apply -f mysql-deployment.yaml
sleep 4
kubectl apply -f ser_collect_data.yaml
sleep 4
kubectl apply -f ser_dashboard.yaml
sleep 4
kubectl apply -f ser_get_devices_stat.yaml
sleep 4
kubectl apply -f job_db_instantiate.yaml
sleep 4
kubectl apply -f job_db_dump.yaml
sleep 4
kubectl apply -f job_dump_upload.yaml
sleep 4
kubectl apply -f dep_collect_data.yaml
sleep 4
kubectl apply -f dep_dashboard.yaml
sleep 4
kubectl apply -f dep_get_devices_stat.yaml
sleep 4
kubectl apply -f dep_calculate_value.yaml
sleep 4
kubectl apply -f cronjob_check_devices_status.yaml
minikube tunnel