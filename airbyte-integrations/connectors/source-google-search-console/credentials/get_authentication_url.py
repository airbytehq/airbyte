#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

# Check https://developers.google.com/webmaster-tools/search-console-api-original/v3/ for all available scopes
OAUTH_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"

with open("credentials.json", "r") as f:
    credentials = json.load(f)

CLIENT_ID = credentials.get("client_id")
CLIENT_SECRET = credentials.get("client_secret")
REDIRECT_URI = credentials.get("redirect_uri")

authorize_url = (
    f"https://accounts.google.com/o/oauth2/v2/auth"
    f"?response_type=code"
    f"&access_type=offline"
    f"&prompt=consent&client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope={OAUTH_SCOPE}"
)
print(f"Go to the following link in your browser: {authorize_url} and copy code from URL")
