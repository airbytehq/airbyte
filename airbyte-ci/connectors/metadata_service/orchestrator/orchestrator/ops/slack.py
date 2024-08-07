#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

from dagster import OpExecutionContext, op
from dagster_slack import SlackResource
from slack_sdk import WebhookClient


def chunk_messages(report):
    """split report into messages with no more than 4000 chars each (slack limitation)"""
    msg = ""
    for line in report.splitlines():
        msg += line + "\n"
        if len(msg) > 3500:
            yield msg
            msg = ""
    yield msg


def send_slack_message(context: OpExecutionContext, channel: str, message: str, enable_code_block_wrapping: bool = False):
    """
    Send a slack message to the given channel.

    Args:
        context (OpExecutionContext): The execution context.
        channel (str): The channel to send the message to.
        message (str): The message to send.
    """
    if os.getenv("SLACK_TOKEN") and os.getenv("SLACK_NOTIFICATIONS_DISABLED") != "true":
        # Ensure that a failure to send a slack message does not cause the pipeline to fail
        try:
            for message_chunk in chunk_messages(message):
                if enable_code_block_wrapping:
                    message_chunk = f"```{message_chunk}```"

                context.resources.slack.get_client().chat_postMessage(channel=channel, text=message_chunk)
        except Exception as e:
            context.log.info(f"Failed to send slack message: {e}")
