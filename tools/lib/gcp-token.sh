#!/usr/bin/env bash
# Test script to access/generate secrets in Secret Manager

# PROJECT="engineering-devops"
# SCOPE="https://www.googleapis.com/auth/cloud-platform"
# SERVICE_ACCOUNT_FILE=secret-manager.json
# SECRET=my-secret
TOKEN_TTL=3600


_var2base64() {
  printf "$1" | _urlencode_base64
}

_urlencode_base64() {
  base64 | tr '/+' '_-' | tr -d '=\n'
}

function _parse_token_uri(){
  local config_file=$1
  local token_uri=$(jq -r .token_uri ${config_file})
  echo "${token_uri}"
}

function _generate_jwt() {
  # Generate JWT token by a service account json file and scopes
  local config_file=$1
  local scopes=$2

  local now="$(date +%s)"
  local expiration_time=$((${now} + ${TOKEN_TTL}))
  # parse a file with credentials 
  local private_key=$(jq -r .private_key ${config_file})
  local client_email=$(jq -r .client_email ${config_file})
  local token_uri=$(_parse_token_uri "${config_file}")
  
  local claim=$(echo "{
    \"iat\": ${now},
    \"iss\": \"${client_email}\",
    \"scope\": \"$scopes\",
    \"aud\": \"${token_uri}\",
    \"exp\":${expiration_time}
  }" | jq -c)
  local headers='{"typ":"JWT","alg":"RS256"}'
  local body="$(_var2base64 "$headers").$(_var2base64 "$claim")"
  local signature=$(openssl dgst -sha256 -sign <(echo "$private_key") <(printf "$body") | _urlencode_base64)
  echo "$body.$signature"
}

function parse_project_id(){
  # find a project_id into config file
  local config_file=$1
  local project_id=$(jq -r .project_id ${config_file})
  echo "${project_id}"
}

function get_gcp_access_token() {
  # Generate an access token by a service account json file and scopes
  local config_file="$1"
  local scopes="$2"
  local jwt=`_generate_jwt "${config_file}" "$scopes"`
  local token_uri=$(_parse_token_uri "${config_file}")
  local data=$(curl -s -X POST ${token_uri} \
    --data-urlencode "assertion=${jwt}" \
    --data-urlencode 'grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer'
    )
  echo $data | jq -r .access_token
}

