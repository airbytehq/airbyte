import requests

from .base_request import BaseRequest


class HttpRequest(BaseRequest):
    def __init__(self, options):
        super().__init__(options)

    def build(self):
        return {
            'method': self.options.get('method', 'get'),
            'url': self.options['base_url']
        }
