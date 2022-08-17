#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

filename='./changed_files.txt'
n=1
while read line; do
# reading each line
echo "Line No. $n : $line"
n=$((n+1))
done < $filename