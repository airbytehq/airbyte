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

        state_config = self.options['state']
        self.state = self.strategy_builder(state_config['strategy'], state_config['options'], **kwargs)

    def extract(self, context):
        context = {
            'config': context.get('config'),
            'state': context.get('state'),
            'var': context.get('var'),
        }

        state = None

        for page in self.pagination.iterate(context):
            context['page'] = page

            request_params = self.request.build(context)

            response = requests.request(**request_params)

            state = self.state.get(context)

            logging.debug(response.json())
            logging.debug(state)
