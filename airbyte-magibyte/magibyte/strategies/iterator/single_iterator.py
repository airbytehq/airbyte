from .base_iterator import BaseIterator


class SingleIterator(BaseIterator):
    def __init__(self, **kwargs):
        super(SingleIterator, self).__init__(**kwargs)

    def iterate(self, context):
        yield {}
