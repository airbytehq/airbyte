#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import json
import typing

import requests

from pipelines import main_logger

if typing.TYPE_CHECKING:
    from typing import List


def send_message_to_webhook(message: str, channels: List[str], webhook: str) -> List[requests.Response]:
    responses = []
    for channel in channels:
        channel = channel[1:] if channel.startswith("#") else channel
        payload = {"channel": f"#{channel}", "username": "Connectors CI/CD Bot", "text": message}
        response = requests.post(webhook, data={"payload": json.dumps(payload)})

        # log if the request failed, but don't fail the pipeline
        if not response.ok:
            main_logger.error(f"Failed to send message to slack webhook: {response.text}")
        responses.append(response)

    return responses
