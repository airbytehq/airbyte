#!/bin/bash

# Check if the file name is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

# The file to be split
FILENAME=$1

# Counter for batch files
COUNTER=1

# Split the file. Each chunk will have 20 lines.
# Files will be named as 'x00', 'x01', ...
split -l 20 $FILENAME temp_batch

# Rename files to batch1.txt, batch2.txt, ...
for file in temp_batch*; do
    mv "$file" "to_check_batch$COUNTER.txt"
    let COUNTER=COUNTER+1
done

echo "File split successfully."
