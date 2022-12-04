#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import argparse
import concurrent.futures
import json
import logging
import os
from typing import Dict, List, Sequence, Tuple, Union
from urllib.parse import urljoin

import requests as requests

# TODO: unit-tests
# TODO: combine URL according to a region from config
API_URL = "https://api.mailgun.net/v3/"


# TODO: add more fields for sending messages: cc, bcc, o:*, h:*, v:*, etc.


class DataFiller:
    def __init__(self, from_emails, to, number_of_messages, logger=None, **kwargs):
        config_file = kwargs.get("config_file", os.path.join(os.path.dirname(__file__), os.pardir, "secrets", "config.json"))
        with open(config_file) as fp:
            config = json.load(fp)
        self.api_key = config["private_key"]
        self.domains = self.get_domains()
        self.senders = from_emails
        self.recipients = to
        self.number = number_of_messages

        self.logger = logger or logging.getLogger("Data Filler")

    def fill(self):
        self.send_messages(self.domains, self.senders, self.recipients)

    def get_domains(self) -> Tuple[str]:
        domains_url = urljoin(API_URL, "domains")
        response = requests.get(domains_url, auth=("api", self.api_key))
        domains: Tuple[str] = tuple(item["name"] for item in response.json()["items"])  # type: ignore[assignment]
        return domains

    def post_request(self, url, data):
        return requests.post(url, auth=("api", self.api_key), data=data)

    def send_messages(self, domains: Sequence[str], senders: Sequence[str], recipients: Sequence[str]):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(domains) * len(senders) * self.number) as executor:
            future_responses = {}
            for domain in domains:
                url: str = urljoin(urljoin(API_URL, f"{domain}/"), "messages")
                for sender in senders:
                    for i in range(self.number):
                        data: Dict[str, Union[str, List[str]]] = {
                            "from": f"{sender} <{sender}@{domain}>",
                            "to": recipients,
                            "subject": f"Test message #{i} from {sender}",
                            "text": f"Hello! It is an amazing test message #{i}!",  # TODO: create full messages
                        }
                        future_responses[executor.submit(self.post_request, url, data)] = (sender, recipients)
            for future in concurrent.futures.as_completed(future_responses):
                sender, recipients = future_responses[future]
                response = future.result()
                if response.ok:
                    self.logger.info(f"Message #{i} from {sender} to {recipients} was successfully sent")
                else:
                    self.logger.warning(response.reason)  # TODO: Make more informative output


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Populate test data for Mailgun sandbox")

    parser.add_argument("-f", "--from-emails", action="append", help="List of senders' names", required=True)
    parser.add_argument(
        "-t",
        "--to",
        action="append",
        help="List of recipients (must be defined as 'Authorized recipients' in the Mailgun sandbox",
        required=True,
    )
    parser.add_argument(
        "-n", "--number-of-messages", type=int, default=5, help="Number of messages to send for every sender-recipient pair"
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    data_filler = DataFiller(**vars(args))
    data_filler.fill()
