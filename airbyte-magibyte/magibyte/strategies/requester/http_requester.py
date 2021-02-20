import logging

import requests

from .base_requester import BaseRequest


class HttpRequest(BaseRequest):
    def __init__(self, options, **kwargs):
        super(HttpRequest, self).__init__(options, **kwargs)

        self.decoder = self.build_strategy('decoder', options['decoder'], **kwargs)
        self.paginator = self.build_strategy('paginator', options['paginator'], **kwargs)
        self.shaper = self.build_strategy('shaper', options['shaper'], **kwargs)

    def request(self, context):

        for page in self.paginator.paginate(context):
            context['page'] = page

            context['request'] = self._build_request(context)
            # logging.debug(f'request: {context["request"]}')

            context['response'] = requests.request(**context['request'])
            # logging.debug(context['response'])

            context['decoded_response'] = self.decoder.decode(context.copy())

            # logging.debug(context['decoded_response'])

            for record in self.shaper.shape(context.copy()):
                yield record

    def _build_request(self, context):
        # create a `requests` compatible object
        request = {
            'method': self.extrapolate(self.options.get('method', 'get'), context),
            'url': self.extrapolate(self.options['base_url'], context),
            'params': self._extract_options('params', context),
            'headers': {k: v for (k, v) in self._extract_options('headers', context)},
        }

        return request

    def _extract_options(self, http_object, context):
        res = []
        for param in self.options.get(http_object, []):
            name = self.extrapolate(param.get('name'), context)
            value = self.extrapolate(param.get('value'), context)
            if value or self.extrapolate(param.get('on_empty'), context) != 'skip':
                res.append((name, value))
        return res
