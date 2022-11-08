#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import sys
from urllib.parse import unquote

import requests

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

with open("credentials.json", "r") as f:
    credentials = json.load(f)

CLIENT_ID = credentials.get("client_id")
CLIENT_SECRET = credentials.get("client_secret")
REDIRECT_URI = credentials.get("redirect_uri")

code = str(sys.argv[1]).strip()
code = unquote(code)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
}

params = {
    "grant_type": "authorization_code",
    "code": code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
}

response = requests.post(url=GOOGLE_TOKEN_URL, params=params, headers=headers)
print(f'refresh token - {response.json().get("refresh_token")}')
