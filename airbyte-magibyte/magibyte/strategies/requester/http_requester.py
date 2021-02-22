import logging

import requests

from .base_requester import BaseRequest
from ..decoder.json_decoder import JsonDecoder
from ..paginator.noop_paginator import NoopPaginator
from ..shaper.identity_shaper import IdentityShaper


class HttpRequest(BaseRequest):
    def __init__(self, options, **kwargs):
        super(HttpRequest, self).__init__(options, **kwargs)

        if 'decoder' not in options:
            self.decoder = JsonDecoder({}, **kwargs)
        else:
            self.decoder = self.build_strategy('decoder', options['decoder'], **kwargs)

        if 'paginator' not in options:
            self.paginator = NoopPaginator({}, **kwargs)
        else:
            self.paginator = self.build_strategy('paginator', options['paginator'], **kwargs)

        if 'shaper' not in options:
            self.shaper = IdentityShaper({}, **kwargs)
        else:
            self.shaper = self.build_strategy('shaper', options['shaper'], **kwargs)

    def request(self, context):
        for page in self.paginator.paginate(context.copy()):
            context['page'] = page

            request = self._build_request(context)
            context['request'] = request
            # logging.debug(f"request: {request}")

            response = requests.request(**request)
            context['response'] = response
            # logging.debug(f"response: {response}")

            decoded_response = self.decoder.decode(context.copy())
            context['decoded_response'] = decoded_response
            # logging.debug(f"decoded_response: {decoded_response}")

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
