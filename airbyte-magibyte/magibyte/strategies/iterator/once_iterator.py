from .base_iterator import BaseIterator


class Onceterator(BaseIterator):
    def __init__(self, **kwargs):
        super(Onceterator, self).__init__(**kwargs)

    def iterate(self, context):
        yield {}
