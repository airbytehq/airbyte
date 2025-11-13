#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
import os
from typing import Generator, Optional

from slack_sdk import WebClient

from metadata_service.constants import SLACK_NOTIFICATIONS_ENABLED

logger = logging.getLogger(__name__)


def _chunk_messages(message: str) -> Generator[str, None, None]:
    """Split message into messages with no more than 3992 chars each. Slack will automatically split any messages that are 4000 chars or more."""
    slack_message_char_limit = 3992
    msg = ""
    for line in message.splitlines():
        if len(msg + line + "\n") > slack_message_char_limit:
            yield msg
        msg += line + "\n"
    yield msg


def send_slack_message(channel: str, message: str, enable_code_block_wrapping: bool = False) -> tuple[bool, Optional[str]]:
    """
    Send a slack message to the given channel.

    Args:
        channel (str): The channel to send the message to.
        message (str): The message to send.

    Returns:
        tuple[bool, str]: (success, error_message)
    """
    if (slack_token := os.environ.get("SLACK_TOKEN")) and SLACK_NOTIFICATIONS_ENABLED == "true":
        # Ensure that a failure to send a slack message does not cause the pipeline to fail
        try:
            slack_client = WebClient(token=slack_token)
            for message_chunk in _chunk_messages(message):
                if enable_code_block_wrapping:
                    message_chunk = f"```{message_chunk}```"

                slack_client.chat_postMessage(channel=channel, text=message_chunk)
            return True, None
        except Exception as e:
            logger.error(f"Failed to send slack message: {e}")
            return False, str(e)
    elif not slack_token:
        logger.info("Slack token is not set - skipping message send")
    else:
        logger.info("Slack notifications are disabled - skipping message send")
    return True, None
