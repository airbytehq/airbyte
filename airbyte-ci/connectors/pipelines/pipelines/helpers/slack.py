#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import requests
from pipelines import main_logger


def send_message_to_webhook(message: str, channel: str, webhook: str) -> requests.Response:
    payload = {"channel": f"#{channel}", "username": "Connectors CI/CD Bot", "text": message}
    response = requests.post(webhook, data={"payload": json.dumps(payload)})

    # log if the request failed, but don't fail the pipeline
    if not response.ok:
        main_logger.error(f"Failed to send message to slack webhook: {response.text}")

    return response
