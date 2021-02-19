import logging

from .base_extractor import BaseExtractor


class SimpleExtractor(BaseExtractor):
    def __init__(self, **kwargs):
        super(SimpleExtractor, self).__init__(**kwargs)

        self.requester = self._build_step('requester', **kwargs)
        self.iterator = self._build_step('iterator', **kwargs)
        self.state = self._build_step('state', **kwargs)

    def extract(self, context):
        state = None

        for cursor in self.iterator.iterate(context.copy()):
            context['cursor'] = cursor

            for record in self.requester.request(context.copy()):
                logging.debug(record)
                context['record'] = record
                state = self.state.get(context.copy())

        logging.debug(state)
