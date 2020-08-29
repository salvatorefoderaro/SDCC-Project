#!/bin/bash

cd ../Server
clear
kubectl delete deployment collectdatadeployment
kubectl delete deployment dashboarddeployment
kubectl delete deployment dbconnectordeployment
kubectl delete job dbinstantiate
kubectl delete cronjobs jobdbdump
kubectl delete job uploads3job
kubectl delete cronjobs checkstatusjob
kubectl delete deployment sendemaildeployment
kubectl delete deployment calculatevaluedeployment
cp cluster_config.json dashboard/cluster_config.json
cp cluster_config.json s3_upload_dump/cluster_config.json
cp cluster_config.json calculate_value/cluster_config.json
eval $(minikube docker-env)
cd check_devices_status && docker build -t checkdevicestatus:v1 .
cd ../collect_data && docker build -t collectdata:v1 .
cd ../instantiate_database && docker build -t dbinstantiate:v1 .
cd ../dashboard && docker build -t dashboard:v1 .
cd ../db_connector && docker build -t dbconnector:v1 .
cd ../s3_upload_dump && docker build -t uploads3:v1 .
cd ../send_email && docker build -t sendemail:v1 .
cd ../calculate_value_aws && docker build -t calculatevalue:v1 .
cd ../yaml
docker pull mysql:5.7.5
kubectl apply -f job_db_instantiate.yaml
kubectl apply -f job_db_dump.yaml
kubectl apply -f job_dump_upload.yaml
kubectl apply -f dep_collect_data.yaml
kubectl apply -f dep_dashboard.yaml
kubectl apply -f dep_db_connector.yaml
kubectl apply -f dep_calculate_value.yaml
kubectl apply -f cronjob_check_devices_status.yaml
kubectl apply -f dep_send_email.yaml
minikube tunnel