from functools import reduce

from .base_request import BaseRequest

"""
options:
    base_url: https://{config.account_id}.service.io/api/{var.name}
    method: GET # get could be the default but we expose it for POST type of queries
    headers:
    - name: x-api-key
      value: my_value
    params:
    - name: date
      value: my_param
      on_empty: skip
"""


class HttpRequest(BaseRequest):
    def build(self, context):
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
