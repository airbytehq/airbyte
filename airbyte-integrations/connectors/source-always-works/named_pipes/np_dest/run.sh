#!/usr/bin/env bash

while IFS='$\n' read -r line; do
    echo "received $line"
done
