from .base_decoder import BaseDecode


class JsonDecoder(BaseDecode):
    def decode(self, context):
        return context['response'].json()
