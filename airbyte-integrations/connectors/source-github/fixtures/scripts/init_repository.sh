#!/bin/bash

if git status
then
  echo "Repository already initialized"
elif [ ! "$1" ]
then
    echo "No repository url was provided"
else
  git init
  git remote add origin "$1"
  echo "Initialized repository $1"
fi