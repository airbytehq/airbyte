import jmespath

from .base_shaper import BaseSelect


class JMESPathShaper(BaseSelect):
    def shape(self, context):
        decoded_data = context['decoded_response']

        path = self.extrapolate(self.options.get('path'), context)

        # The output of the shaped data should always be a list. If it is not the case then last make it one.
        shaped_data = jmespath.search(path, decoded_data)
        if type(shaped_data) == dict:
            shaped_data = [shaped_data]

        for m in shaped_data:
            yield m
