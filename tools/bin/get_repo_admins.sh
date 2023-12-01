#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <personal_access_token> <repository>"
    exit 1
fi

# Assign arguments to variables
TOKEN="$1"
REPO="$2"

# GitHub API URL for repository collaborators
API_URL="https://api.github.com/repos/$REPO/collaborators"

# Curl command to get the list of collaborators with admin rights
curl -H "Authorization: token $TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     "$API_URL" | jq '.[] | select(.permissions.admin == true) | "[\(.login)](\(.html_url)),"' | tr -d '"' | paste -sd " " -
