#!/bin/bash

clear
kubectl delete deployment collectdatadeployment
kubectl delete deployment dashboarddeployment
kubectl delete deployment getdevicesstatdeployment
kubectl delete job dbinstantiate
kubectl delete cronjob jobdbdump
kubectl delete cronjobs uploads3job
kubectl delete secrets mysql-secrets
kubectl delete cronjobs checkstatusjob
kubectl delete cronjobs calculatevaluejob
kubectl delete services getdevicesstatservice
kubectl delete services dashboardservice
kubectl delete services collectdataservice
kubectl delete services mysql
kubectl delete deployment mysql