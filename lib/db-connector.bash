#!/bin/bash


DBHOST="$1"
DBPORT="$2"
DBNAME="$3"
OPERATION="$4"
DATAFACTOR="$5"

MYID="$OMPI_COMM_WORLD_RANK"
MYCONNLOG="executors/nopaw.connector.$MYID.out"
MYEXECLOG="executors/nopaw.executor.$MYID.out"

echo "My ID $MYID"     >> $MYCONNLOG
echo "I'm a connector" >> $MYCONNLOG
echo "My Python: $(which python)" >> $MYCONNLOG
echo "My args $@" >> $MYCONNLOG
echo "a connector starts `date +%Y/%m/%d-%H:%M:%S.%5N`" >> $MYCONNLOG

mongo-executor.py "$DBHOST" "$DBPORT" "$DBNAME" "$DATAFACTOR" >> $MYEXECLOG

echo "a connector stops `date +%Y/%m/%d-%H:%M:%S.%5N`" >> $MYCONNLOG
