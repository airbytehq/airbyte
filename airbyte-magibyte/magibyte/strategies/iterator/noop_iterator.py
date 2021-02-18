from .base_iterator import BaseIterator


class NoopIterator(BaseIterator):
    def __init__(self, **kwargs):
        super(NoopIterator, self).__init__(**kwargs)

    def iterate(self, context):
        pass
