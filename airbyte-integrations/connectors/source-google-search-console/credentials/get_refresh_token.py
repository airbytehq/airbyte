#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
