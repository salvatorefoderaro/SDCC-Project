#!/bin/bash

kubectl delete pods mysql-client
kubectl run -it --rm --image=mysql:latest --restart=Never mysql-client -- mysql -h mysql -ppassword
