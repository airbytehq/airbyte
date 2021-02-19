import pyjq

from .base_shaper import BaseSelect


class JQShaper(BaseSelect):
    def shape(self, context):
        decoded_data = context['decoded_response']

        script = self.extrapolate(self.options.get('script', '.'), context)

        # The output of the shaped data should always be a list. If it is not the case then last make it one.
        shaped_data = pyjq.all(script, decoded_data)

        for m in shaped_data:
            yield m
