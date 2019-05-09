#!/bin/bash

NETDEVICE="$1"
DBLOCATION="$2"

echo "a ghost writer starts `date +%Y/%m/%d-%H:%M:%S.%5N`"
# Parse the ip address for given NETDEVICE
DBHOST=`ip addr show $NETDEVICE | grep -Eo '(addr:)?([0-9]*\.){3}[0-9]*' | head -n1`
echo "Writing Mongo Host IP: $DBHOST"
echo "to file: $DBLOCATION/hostname.txt"
echo "$DBHOST" > $DBLOCATION/hostname.txt
# Lightweight blocking command
sleep infinity
echo "a ghost writer stops `date +%Y/%m/%d-%H:%M:%S.%5N`"
