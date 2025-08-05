#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
import os
from typing import Generator

from slack_sdk import WebClient

logger = logging.getLogger(__name__)


SLACK_MESSAGE_CHAR_LIMIT = 4000


def _chunk_messages(message: str) -> Generator[str, None, None]:
    """split message into messages with no more than 4000 chars each (slack limitation)"""
    msg = ""
    for line in message.splitlines():
        msg += line + "\n"
        if len(msg) > SLACK_MESSAGE_CHAR_LIMIT:
            yield msg
            msg = ""
    yield msg


def send_slack_message(channel: str, message: str, enable_code_block_wrapping: bool = False) -> None:
    """
    Send a slack message to the given channel.

    Args:
        channel (str): The channel to send the message to.
        message (str): The message to send.
    """
    if slack_token := os.getenv("SLACK_TOKEN") and os.getenv("SLACK_NOTIFICATIONS_DISABLED") != "true":
        # Ensure that a failure to send a slack message does not cause the pipeline to fail
        try:
            slack_client = WebClient(token=slack_token)
            for message_chunk in _chunk_messages(message):
                if enable_code_block_wrapping:
                    message_chunk = f"```{message_chunk}```"

                slack_client.chat_postMessage(channel=channel, text=message_chunk)
        except Exception as e:
            logger.info(f"Failed to send slack message: {e}")
