#!/bin/bash

docker rm $(docker ps -a | grep "python /airbyte/int" | awk '{print $1}')
