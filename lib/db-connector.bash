#!/bin/bash

MYID="$OMPI_COMM_WORLD_RANK"
MYLOG="nopaw.executor.$MYID.out"

echo "I'm a connector" >> $MYLOG
echo "a connector starts `date +%Y/%m/%d-%H:%M:%S.%5N`" >> $MYLOG
sleep 60
echo "a connector stops `date +%Y/%m/%d-%H:%M:%S.%5N`" >> $MYLOG
