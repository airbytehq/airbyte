

from slack_sdk import WebhookClient
from slack_sdk.errors import SlackApiError

# os.environ["SLACK_BUILD_REPORT"]
def send_report(report, webhook_url):
    webhook = WebhookClient(webhook_url)
    try:

        def chunk_messages(report):
            """split report into messages with no more than 4000 chars each (slack limitation)"""
            msg = ""
            for line in report.splitlines():
                msg += line + "\n"
                if len(msg) > 3500:
                    yield msg
                    msg = ""
            yield msg

        for msg in chunk_messages(report):
            webhook.send(text=f"```{msg}```")
        print("Report has been sent")
    except SlackApiError as e:
        print("Unable to send report")
        assert e.response["error"]
