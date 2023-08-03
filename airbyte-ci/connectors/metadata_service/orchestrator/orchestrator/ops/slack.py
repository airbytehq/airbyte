import os

from dagster import op, OpExecutionContext
from slack_sdk import WebhookClient
from dagster_slack import SlackResource


def chunk_messages(report):
    """split report into messages with no more than 4000 chars each (slack limitation)"""
    msg = ""
    for line in report.splitlines():
        msg += line + "\n"
        if len(msg) > 3500:
            yield msg
            msg = ""
    yield msg


@op
def send_slack_webhook(webhook_url, report):
    webhook = WebhookClient(webhook_url)
    for msg in chunk_messages(report):
        # Wrap in code block as slack does not support markdown in webhooks
        webhook.send(f"```{msg}```")


def send_slack_message(context: OpExecutionContext, channel: str, message: str):
    """
    Send a slack message to the given channel.

    Args:
        context (OpExecutionContext): The execution context.
        channel (str): The channel to send the message to.
        message (str): The message to send.
    """
    if os.getenv("SLACK_TOKEN"):
        # Ensure that a failure to send a slack message does not cause the pipeline to fail
        try:
            context.resources.slack.get_client().chat_postMessage(channel=channel, text=message)
        except Exception as e:
            context.log.info(f"Failed to send slack message: {e}")
