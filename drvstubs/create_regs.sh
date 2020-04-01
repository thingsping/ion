#!/bin/bash

if [ -z "$1" ]
then 
  echo "Usage $0 <srvaddr>"
  exit
fi

srvaddr=$1
ctr=1
while [ $ctr -le 9 ]
do
(cat<<ENL 
{ 
    "Key" : "keyIdev$ctr", "Type": "Register", "Nid" : "Idev$ctr", 
    "From" : "10.1.1.10$ctr", "Expires" : 3600, "Mid" : "Idev${ctr}_1"
}
ENL
)>datain.tmp

(cat<<ENDL
{ 
    "Key" : "keyOdev$ctr", "Type": "Register", "Nid" : "Odev$ctr", 
    "From" : "10.1.1.20$ctr", "Expires" : 3600, "Mid" : "Odev${ctr}_1"
}
ENDL
)>dataout.tmp 

    curl   http://$srvaddr -H "Content-Type: application/json" -X POST  -d '@datain.tmp'
    curl   http://$srvaddr -H "Content-Type: application/json" -X POST  -d '@dataout.tmp'

    let ctr=ctr+1 
done 

ctr=10
while [ $ctr -le 10 ]
do
(cat<<ENL 
{ 
    "Key" : "keyIdev$ctr", "Type": "Register", "Nid" : "Idev$ctr", 
    "From" : "10.1.1.1$ctr", "Expires" : 3600, "Mid" : "Idev${ctr}_1"
}
ENL


)>datain.tmp

(cat<<ENDL
{ 
    "Key" : "keyOdev$ctr", "Type": "Register", "Nid" : "Odev$ctr", 
    "From" : "10.1.1.2$ctr", "Expires" : 3600, "Mid" : "Odev${ctr}_1"
}
ENDL
)>dataout.tmp
    curl  http://$srvaddr -H "Content-Type: application/json" -X POST  -d '@datain.tmp'
    curl  http://$srvaddr -H "Content-Type: application/json" -X POST  -d '@dataout.tmp'
    let ctr=ctr+1 
done 
