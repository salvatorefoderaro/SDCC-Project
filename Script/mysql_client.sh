#!/bin/bash

clear
kubectl delete pods mysql-client
kubectl run -it --rm --image=mysql:5.7.5 --restart=Never mysql-client -- mysql -h mysql -ppassword
