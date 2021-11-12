#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
