#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

## Helper functions

random_hex_string() {
  hexdump -vn16 -e'4/4 "%08X" 1 "\n"' /dev/urandom
}

# TODO: pass parameters instead of reading global variables.
signup_for_cloud() {
  curl -s -d '{"returnSecureToken": "true", "email": "'$FAKE_EMAIL'", "password": "'$PASSWORD'"}' -X POST -H "Content-Type: application/json" -H "Referer: https://dev-1-cloud.airbyte.io/" \
    "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyBoso02vygaetaK1nwDa_ZGT_yr3vzldmU"
}

# TODO: pass parameters instead of reading global variables.
create_cloud_user() {
  curl -s -d '{"authProvider": "google_identity_platform", "authUserId": "'$FIREBASE_USER_ID'", "companyName": "Airbyte Integration Tests", "email": "'$FAKE_EMAIL'", "name": "integration tests"}' \
  -X POST -H "Content-Type: application/json" -H "Referrer: https://dev-1-cloud.airbyte.io/" -H "Authorization: Bearer ${AIRBYTE_REMOTE_TEST_AUTH_HEADER}"\
    "https://dev-1-cloud.airbyte.io/cloud/v1/web_backend/users/create"
}

# Create a new user through Firebase.
PASSWORD=`random_hex_string`
FAKE_EMAIL="fake-email-for-acceptance-tests-`random_hex_string`@example.com"
CLOUD_LOGIN_RESULT=`signup_for_cloud`

# Set env variables (I guess I could pass these directly to the acceptance test invocation instead?)
export AIRBYTE_REMOTE_TEST_AUTH_HEADER=`echo $CLOUD_LOGIN_RESULT | jq -r '.idToken'`
export AIRBYTE_REMOTE_TEST_ENDPOINT="dev-1-cloud.airbyte.io"
FIREBASE_USER_ID=`echo $CLOUD_LOGIN_RESULT | jq -r '.localId'`

# Wait a moment, so I don't have to debug race conditions.
sleep 5

# Make a cloud user and workspace.
CLOUD_USER_CREATE_RESULT=`create_cloud_user`
export AIRBYTE_REMOTE_WORKSPACE_ID=`echo $CLOUD_USER_CREATE_RESULT | jq -r '.defaultWorkspaceId'`

echo "Auth header: ${AIRBYTE_REMOTE_TEST_AUTH_HEADER}"
echo "Endpoint: ${AIRBYTE_REMOTE_TEST_ENDPOINT}"
echo "Workspace id: ${AIRBYTE_REMOTE_WORKSPACE_ID}"

SUB_BUILD=PLATFORM USE_EXTERNAL_DEPLOYMENT=true DEBUG=true JAVA_OPTS="${JAVA_OPTS} -Dlog.level=debug -Djavax.net.debug=all" ./gradlew :airbyte-tests:acceptanceTests --rerun-tasks --debug --scan --tests 'io.airbyte.test.acceptance.BasicAcceptanceTests'
