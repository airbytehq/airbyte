import logging

from .base_extractor import BaseExtractor


class SimpleExtractor(BaseExtractor):
    def __init__(self, options, **kwargs):
        super(SimpleExtractor, self).__init__(options, **kwargs)

        self.requester = self.build_strategy('requester', options['requester'], **kwargs)
        self.iterator = self.build_strategy('iterator', options['iterator'], **kwargs)
        self.state = self.build_strategy('state', options['state'], **kwargs)

    def extract(self, context):
        state = None

        for cursor in self.iterator.iterate(context.copy()):
            context['cursor'] = cursor

            for record in self.requester.request(context.copy()):
                logging.debug(f'record: {record}')
                context['record'] = record
                state = self.state.get(context.copy())

        logging.debug(f"state: {state}")
