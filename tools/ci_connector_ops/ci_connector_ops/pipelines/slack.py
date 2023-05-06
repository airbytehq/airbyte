#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os

import requests


def send_message_to_webhook(message: str, channel: str) -> dict:
    payload = {"channel": f"#{channel}", "username": "Connectors CI/CD Bot", "text": message}
    response = requests.post(os.environ["SLACK_WEBHOOK"], data={"payload": json.dumps(payload)})
    response.raise_for_status()
    return response
