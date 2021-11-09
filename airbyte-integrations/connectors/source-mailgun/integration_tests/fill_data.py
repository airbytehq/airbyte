import argparse
import json
import logging
import os.path
from datetime import datetime, timedelta
from typing import Tuple, Dict, Union, List, Iterable
from urllib.parse import urljoin

import requests as requests

now = datetime.now()
begin = now - timedelta(2)

# TODO: combine URL according to a region from config
API_URL = 'https://api.mailgun.net/v3/'


# TODO: add more fields for sending messages: cc, bcc, o:*, h:*, v:*, etc.


class DataFiller:

    def __init__(self, **kwargs):
        config_file = kwargs.get('config_file', os.path.join(os.path.pardir, 'secrets', 'config.json'))
        with open(config_file) as fp:
            config = json.load(fp)
        self.api_key = config['private_key']
        self.domains = self.get_domains()
        self.senders = kwargs['from']
        self.recipients = kwargs['to']
        self.number = kwargs['number_of_messages']

    def fill(self):
        self.send_messages(self.domains, self.senders, self.recipients)

    def get_domains(self) -> Tuple[str]:
        domains_url = urljoin(API_URL, 'domains')
        response = requests.get(domains_url, auth=('api', self.api_key))
        domains: Tuple[str] = tuple(item['name'] for item in response.json()['items'])  # type: ignore[assignment]
        return domains

    def send_messages(self, domains: Iterable[str], senders: Iterable[str], recipients: Iterable[str]):
        for domain in domains:
            url: str = urljoin(urljoin(API_URL, f'{domain}/'), 'messages')
            for sender in senders:
                for i in range(self.number):
                    data: Dict[str, Union[str, List[str]]] = {
                        'from': f'{sender} <{sender}@{domain}>',
                        'to': recipients,
                        'subject': f'Test message #{i} from {sender}',
                        'text': f'Hello! It is an amazing test message #{i}!'  # TODO: create full messages
                    }
                    response = requests.post(
                        url,
                        auth=('api', self.api_key),
                        data=data
                    )
                    if response.ok:
                        logger.info(f"Message #{i} from {sender} to {recipients} was successfully sent")
                    else:
                        logger.warning(response.reason)  # TODO: Make more informative output


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Populate test data for Mailgun sandbox")

    parser.add_argument("-f", "--from", action="append", help="List of senders' names", required=True)
    parser.add_argument("-t", "--to", action="append",
                        help="List of recipients (must be defined as 'Authorized recipients' in the Mailgun sandbox",
                        required=True)
    parser.add_argument("-n", "--number-of-messages", type=int, default=5,
                        help="Number of messages to send for every sender-recipient pair")

    args = parser.parse_args()

    logger = logging.getLogger('Data Filler')
    logging.basicConfig(level=logging.INFO)

    data_filler = DataFiller(**vars(args))
    data_filler.fill()
