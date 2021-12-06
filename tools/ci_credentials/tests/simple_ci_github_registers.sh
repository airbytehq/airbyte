#!/usr/bin/env bash

# some unknown code lines
npvnvpvnwvwv vmw[vanwmvawnvwavw
awvpwnvp-avawvw
awvawvwneavwenav-awe vwevewv-ewanvw-eavnwevwea]


read_secrets source-trello "$SOURCE_TRELLO_TEST_CREDS" "credentials.json"
read_secrets source-trello "$SOURCE_TRELLO_AUTH_CREDS" "auth.json"

read_secrets source-github-gsm "$SOURCE_BIGQUERY_AUTH_CREDS" "auth.json"

exit $?

