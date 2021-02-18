from .base_pagination import BasePagination


class SingleIterator(BasePagination):
    def __init__(self, **kwargs):
        super(SingleIterator, self).__init__(**kwargs)

    def iterate(self, context):
        yield {}
