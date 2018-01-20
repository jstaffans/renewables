#!/bin/bash

for file in *.csv;
do
    awk 'NR > 3 {print $0;}' "$file"
done
