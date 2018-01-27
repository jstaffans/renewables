#!/bin/bash

for file in *.csv;
do
    awk 'NR > 1 {print $0;}' "$file"
done
