import requests

from .abstract_request import AbstractRequest


class HttpRequest(AbstractRequest):
    def __init__(self, options):
        super().__init__(options)

    def execute(self, context):
        return requests.request(
            method=self.options.get('method', 'get'),
            url=self.options['base_url'])
