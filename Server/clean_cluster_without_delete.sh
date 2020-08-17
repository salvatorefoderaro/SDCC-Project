#!/bin/bash

kubectl delete deployment collectdatadeployment
kubectl delete deployment dashboarddeployment
kubectl delete deployment getdevicesstatdeployment
kubectl delete job dbinstantiate
kubectl delete job jobdbdump
kubectl delete job uploads3job
kubectl delete secrets mysql-secrets
kubectl delete cronjobs checkstatusjob
kubectl delete services getdevicesstatservice
kubectl delete services dashboardservice
kubectl delete services collectdataservice
kubectl delete services mysql
kubectl delete deployment calculatevaluedeployment 