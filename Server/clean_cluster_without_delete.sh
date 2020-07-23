#!/bin/bash

kubectl delete deployment collectdatadeployment
kubectl delete deployment dashboarddeployment
kubectl delete deployment mysql
kubectl delete deployment getdevicesstatdeployment
kubectl delete job dbinstantiate
kubectl delete job jobdbdump
kubectl delete job uploads3job
kubectl delete cronjobs checkstatusjob
kubectl delete services getdevicesstatservice
kubectl delete services dashboardservice
kubectl delete services collectdataservice
kubectl delete secrets mysql-secrets