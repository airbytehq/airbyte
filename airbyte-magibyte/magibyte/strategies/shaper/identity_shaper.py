from .base_shaper import BaseSelect


class IdentityShaper(BaseSelect):
    def shape(self, context):
        yield context['decoded_response']
