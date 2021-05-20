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

import base64
import json
import os
import sys
import urllib.parse

import requests


def create_person(seed, token):
    url = "https://a.klaviyo.com/api/identify"

    headers = {"Accept": "text/html"}
    email = f"some.email.that.dont.exist.{seed}@airbyte.io"

    data = {
        "token": token,
        "properties": {
            "$email": email,
            "$first_name": f"First Name {seed}",
            "$last_name": f"Last Name {seed}",
            "$city": "Springfield",
            "$region": "Illinois",
        },
    }

    querystring = {"data": base64.urlsafe_b64encode(json.dumps(data).encode()).decode()}

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)

    return email


def create_event(token, email, name):
    url = "https://a.klaviyo.com/api/track"
    headers = {"Accept": "text/html"}

    data = {"token": token, "event": name, "customer_properties": {"$email": email}}

    querystring = {"data": base64.urlsafe_b64encode(json.dumps(data).encode()).decode()}

    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)


def create_global_exclusion(email, api_key):
    url = "https://a.klaviyo.com/api/v1/people/exclusions"

    querystring = {"api_key": api_key}

    payload = urllib.parse.urlencode([("email", email)])
    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

    print(response.text)


def main():
    token = os.getenv("TOKEN")
    api_key = os.getenv("API_KEY")

    person_num = 10
    events_per_person = 5
    global_exclusion_num = 2

    for i in range(person_num):
        email = create_person(i, token=token)
        if i < global_exclusion_num:
            create_global_exclusion(email, api_key=api_key)
        for k in range(events_per_person):
            create_event(email=email, name="Clicked Email", token=token)


if __name__ == "__main__":
    sys.exit(main())
