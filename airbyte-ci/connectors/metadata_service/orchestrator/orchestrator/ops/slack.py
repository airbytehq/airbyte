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


def send_slack_webhook(webhook_url, report, wrap_in_code_block=False):
    webhook = WebhookClient(webhook_url)
    for msg in chunk_messages(report):
        # Wrap in code block as slack does not support markdown in webhooks
        if wrap_in_code_block:
            msg = f"```{msg}```"
        webhook.send(msg)
