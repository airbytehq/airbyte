from .base_pagination import BasePagination


class NoopIterator(BasePagination):
    def __init__(self, **kwargs):
        super(NoopIterator, self).__init__(**kwargs)

    def iterate(self, context):
        pass
