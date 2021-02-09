from .base_decode import BaseDecode


class JsonDecode(BaseDecode):
    def decode(self, context):
        return context['response'].json()
