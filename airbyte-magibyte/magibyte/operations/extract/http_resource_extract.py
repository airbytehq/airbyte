import logging

import requests

from .base_extract import BaseExtract


class HttpResourceExtract(BaseExtract):
    def __init__(self, **kwargs):
        super(HttpResourceExtract, self).__init__(**kwargs)

        request_config = self.options['request']
        self.request = self.strategy_builder(request_config['strategy'], request_config['options'], **kwargs)

        pagination_config = self.options['pagination']
        self.pagination = self.strategy_builder(pagination_config['strategy'], pagination_config['options'], **kwargs)

    def extract(self, context):
        context = {
            'config': context.get('config'),
            'var': context.get('var'),
        }

        for page in self.pagination.iterate(context):
            context['page'] = page

            request_params = self.request.build(context)

            response = requests.request(**request_params)

            logging.debug(response.json())
