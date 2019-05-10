#!/bin/bash

DBHOST="$1"
DBPORT="$2"

MYID="$OMPI_COMM_WORLD_RANK"
MYCONNLOG="executors/nopaw.connector.$MYID.out"
MYEXECLOG="executors/nopaw.executor.$MYID.out"

echo "I'm a connector" >> $MYCONNLOG
echo "a connector starts `date +%Y/%m/%d-%H:%M:%S.%5N`" >> $MYCONNLOG
#mongo-sync.expect "read $DBHOST $DBPORT testdb"
mongo-sync.py "read" "$DBHOST" "$DBPORT" "testdb" >> $MYEXECLOG
sleep 60
echo "a connector stops `date +%Y/%m/%d-%H:%M:%S.%5N`" >> $MYCONNLOG
