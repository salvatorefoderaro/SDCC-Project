#!/bin/bash

eval $(minikube docker-env)
cd check_status_deployment && docker build -t checkstatus:v1 .
cd ../collect_data_deployment && docker build -t collectdata:v1 .
cd ../database_instantiate_job && docker build -t dbinstantiate:v1 .
cd ../dashboard && docker build -t dashboard:v1 .
cd ../get_devices_stat_dashboard && docker build -t getdevicesstat:v1 .
cd ../s3_upload_dump && docker build -t uploads3:v1 .
cd ../yaml
kubectl apply -f job_db_instantiate.yaml
kubectl apply -f dep_collect_data.yaml
kubectl apply -f dep_dashboard.yaml
kubectl apply -f dep_get_devices_stat.yaml
kubectl apply -f cronjob_check_devices_status.yaml
kubectl apply -f job_dump_upload.yaml
