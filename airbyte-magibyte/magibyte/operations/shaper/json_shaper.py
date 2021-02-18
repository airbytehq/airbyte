from .base_shaper import BaseDecode


class JsonShaper(BaseDecode):
    def decode(self, context):
        return context['response'].json()
