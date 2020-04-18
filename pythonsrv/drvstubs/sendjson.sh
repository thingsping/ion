#!/bin/bash

if [ -z "$2" ]
then
  echo "Usage $0 <ccsh server address> <json file_to_send>"
  exit
fi
srvaddr=$1
jsonfile=$2

 curl -v http://$srvaddr -i -H "Content-Type: application/json" -X post -d "@$jsonfile" 
