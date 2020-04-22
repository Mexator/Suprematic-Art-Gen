#!/bin/bash
function swap()         
{
    local TMPFILE=tmp.$$
    mv "$1" $TMPFILE
    mv "$2" "$1"
    mv $TMPFILE "$2"
}
for i in {1..10}
do
    swap input/unnamed.png input/unnamed$i.png
    python main.py
    swap input/unnamed.png input/unnamed$i.png
done
