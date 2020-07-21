#!/bin/bash

minikube start
eval $(minikube docker-env)
cd check_status_deployment && docker build -t checkstatus:v1 .
cd ../collect_data_deployment && docker build -t collectdata:v1 .
cd ../database_instantiate_job && docker build -t dbinstantiate:v1 .
cd ../dashboard && docker build -t dashboard:v1 .
cd ../get_devices_stat_dashboard && docker build -t getdevicesstat:v1 .
cd ../yaml
docker pull mysql:5.7
kubectl apply -f secret.yaml
sleep 10
kubectl apply -f mysql-pv.yaml
sleep 10
kubectl apply -f mysql-deployment.yaml
sleep 10
kubectl apply -f ser_collect_data.yaml
sleep 10
kubectl apply -f ser_dashboard.yaml
sleep 10
kubectl apply -f ser_get_devices_stat.yaml
sleep 10
kubectl apply -f db_instantiate_job.yaml
sleep 10
kubectl apply -f dep_collect_data.yaml
sleep 10
kubectl apply -f dep_dashboard.yaml
sleep 10
kubectl apply -f dep_get_devices_stat.yaml
sleep 10
kubectl apply -f cronjob_check_status.yaml
sleep 10
minikube tunnel