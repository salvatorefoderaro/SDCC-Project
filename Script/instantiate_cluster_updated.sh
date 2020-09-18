#!/bin/bash

cd ../Fog_Cluster
minikube start --driver=docker
minikube addons enable storage-provisioner
minikube addons enable metrics-server
minikube addons enable freshpod
eval $(minikube docker-env)
cp cluster_config.json dashboard/cluster_config.json
cp cluster_config.json s3_upload_dump/cluster_config.json
cp cluster_config.json calculate_value_aws/cluster_config.json
cp cluster_config.json send_email/cluster_config.json
cp s3_key.json dashboard/s3_key.json
cp s3_key.json s3_upload_dump/s3_key.json
cd check_devices_status && docker build -t checkdevicestatus:v1 .
cd ../collect_data && docker build -t collectdata:v1 .
cd ../instantiate_database && docker build -t dbinstantiate:v1 .
cd ../dashboard && docker build -t dashboard:v1 .
cd ../db_connector && docker build -t dbconnector:v1 .
cd ../s3_upload_dump && docker build -t uploads3:v1 .
cd ../send_email && docker build -t sendemail:v1 .
cd ../calculate_value_aws && docker build -t calculatevalue:v1 .
cd ../ssdp_server && docker build -t ssdpserver:v1 .
cd ..
rm dashboard/cluster_config.json
rm s3_upload_dump/cluster_config.json
rm calculate_value_aws/cluster_config.json
rm dashboard/s3_key.json
rm s3_upload_dump/s3_key.json
rm send_email/cluster_config.json
docker pull mysql:5.7.5
cd yaml
kubectl apply -f secret.yaml
kubectl apply -f mysql-dump.yaml
kubectl apply -f mysql-pv.yaml
kubectl apply -f mysql-deployment.yaml
sleep 30
kubectl apply -f ser_collect_data.yaml
kubectl apply -f ser_dashboard.yaml
kubectl apply -f ser_db_connector.yaml
kubectl apply -f job_db_instantiate.yaml
kubectl apply -f cronjob_db_dump.yaml
kubectl apply -f cronjob_dump_upload.yaml
kubectl apply -f dep_collect_data_hpa.yaml
kubectl apply -f dep_collect_data.yaml
kubectl apply -f dep_dashboard.yaml
kubectl apply -f dep_db_connector.yaml
kubectl apply -f cronjob_calculate_value.yaml
kubectl apply -f cronjob_check_devices_status.yaml
kubectl apply -f ser_send_email.yaml
kubectl apply -f dep_send_email.yaml
kubectl apply -f dep_ssdp_server.yaml
kubectl apply -f ser_ssdp_server.yaml
minikube tunnel