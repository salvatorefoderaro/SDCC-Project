#!/bin/bash

minikube start --driver=docker
minikube addons enable storage-provisioner
minikube addons enable metrics-server
eval $(minikube docker-env)
cp cluster_config.json dashboard/cluster_config.json
cp cluster_config.json s3_upload_dump/cluster_config.json
cd check_devices_status && docker build -t checkdevicestatus:v1 .
cd ../collect_data && docker build -t collectdata:v1 .
cd ../instantiate_database && docker build -t dbinstantiate:v1 .
cd ../dashboard && docker build -t dashboard:v1 .
cd ../get_devices_stat && docker build -t getdevicesstat:v1 .
cd ../s3_upload_dump && docker build -t uploads3:v1 .
cd ../calculate_value && docker build -t calculatevalue:v1 .
cd ../yaml
docker pull mysql:5.7.5
kubectl apply -f secret.yaml
kubectl apply -f mysql-dump.yaml
kubectl apply -f mysql-pv.yaml
kubectl apply -f mysql-deployment.yaml
sleep 60
kubectl apply -f ser_collect_data.yaml
kubectl apply -f ser_dashboard.yaml
kubectl apply -f ser_get_devices_stat.yaml
kubectl apply -f job_db_instantiate.yaml
kubectl apply -f job_db_dump.yaml
kubectl apply -f job_dump_upload.yaml
kubectl apply -f dep_collect_data.yaml
kubectl apply -f dep_dashboard.yaml
kubectl apply -f dep_get_devices_stat.yaml
kubectl apply -f dep_calculate_value.yaml
kubectl apply -f cronjob_check_devices_status.yaml
kubectl apply -f dep_collect_data_hpa.yaml
kubectl apply -f ser_calculate_value.yaml
minikube tunnel