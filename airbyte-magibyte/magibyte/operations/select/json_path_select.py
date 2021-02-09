from jsonpath_rw import parse

from .base_select import BaseSelect


class JsonPathSelect(BaseSelect):
    def select(self, context):
        decoded_data = context['decoded_response']

        path = self.extrapolate(self.options.get('path'), context)
        jsonpath_expr = parse(path)

        for m in jsonpath_expr.find(decoded_data):
            yield m.value
