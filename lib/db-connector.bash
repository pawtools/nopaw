#!/bin/bash

DBHOST="$1"
DBPORT="$2"
DBNAME="$3"
OPERATION="$4"

MYID="$OMPI_COMM_WORLD_RANK"
MYCONNLOG="executors/nopaw.connector.$MYID.out"
MYEXECLOG="executors/nopaw.executor.$MYID.out"

echo "I'm a connector" >> $MYCONNLOG
echo "My Python: $(which python)" >> $MYCONNLOG
echo "a connector starts `date +%Y/%m/%d-%H:%M:%S.%5N`" >> $MYCONNLOG

mongo-sync.py "$OPERATION" "$DBHOST" "$DBPORT" "$DBNAME" >> $MYEXECLOG

sleep 60
echo "a connector stops `date +%Y/%m/%d-%H:%M:%S.%5N`" >> $MYCONNLOG
