from .base_iterator import BaseIterator


class NoopIterator(BaseIterator):
    def iterate(self, context):
        pass
