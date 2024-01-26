#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import requests


def query_endpoint(endpoint):
    try:
        response = requests.get("https://" + endpoint)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Failed to query {endpoint}: {e}")
        return None
