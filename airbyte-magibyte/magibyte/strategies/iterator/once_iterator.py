from .base_iterator import BaseIterator


class OnceIterator(BaseIterator):
    def iterate(self, context):
        yield {}
