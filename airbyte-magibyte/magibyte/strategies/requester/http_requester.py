import logging

import requests

from .base_requester import BaseRequest


class HttpRequest(BaseRequest):
    def __init__(self, **kwargs):
        super(HttpRequest, self).__init__(**kwargs)

        self.decoder = self._build_step('decoder', **kwargs)
        self.paginator = self._build_step('paginator', **kwargs)
        self.shaper = self._build_step('shaper', **kwargs)

    def request(self, original_context):
        context = dict(original_context)

        for page in self.paginator.paginate(context):
            context['page'] = page

            context['requester'] = self._build_request(context)
            logging.debug(context['requester'])

            context['response'] = requests.request(**context['requester'])
            context['decoded_response'] = self.decoder.decode(context)

            logging.debug(context['decoded_response'])

            for record in self.shaper.shape(context):
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
