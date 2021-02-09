from .base_pagination import BasePagination


class NoopPagination(BasePagination):
    def __init__(self, **kwargs):
        super(NoopPagination, self).__init__(**kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration()

