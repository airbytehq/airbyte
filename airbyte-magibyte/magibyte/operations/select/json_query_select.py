import jmespath

from .base_select import BaseSelect


class JsonQuerySelect(BaseSelect):
    def select(self, context):
        decoded_data = context['decoded_response']

        path = self.extrapolate(self.options.get('path'), context)

        for m in jmespath.search(path, decoded_data):
            yield m
