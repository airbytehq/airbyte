#!/bin/sh

echo "starting..."

while IFS= read -r line
do
  echo "{\"msg\": \"$line\"}"
  sleep 3
done < "/pipes/file.txt"

echo "ended."
