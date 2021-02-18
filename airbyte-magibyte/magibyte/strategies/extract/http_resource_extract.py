import logging

import requests

from .base_extract import BaseExtract


class HttpResourceExtract(BaseExtract):
    def __init__(self, **kwargs):
        super(HttpResourceExtract, self).__init__(**kwargs)

        self.request = self._build_step('request', **kwargs)
        self.decoder = self._build_step('decoder', **kwargs)
        self.shaper = self._build_step('shaper', **kwargs)
        self.iterator = self._build_step('iterator', **kwargs)
        self.state = self._build_step('state', **kwargs)
        self.request = self._build_step('request', **kwargs)

    def extract(self, context):
        context = {
            'config': context.get('config'),
            'state': context.get('state'),
            'vars': context.get('vars'),
        }

        state = None

        for cursor in self.iterator.iterate(context):
            context['page'] = cursor

            context['request'] = self.request.build(context)
            logging.debug(context['request'])
            context['response'] = requests.request(**context['request'])
            context['decoded_response'] = self.decoder.decode(context)
            logging.debug(context['decoded_response'])

            for record in self.shaper.select(context):
                logging.debug(record)
                context['record'] = record
                state = self.state.get(context)

            logging.debug(state)

    def _build_step(self, name, **kwargs):
        config = self.options[name]
        return self.strategy_builder(config['strategy'], config.get('options', {}), **kwargs)
