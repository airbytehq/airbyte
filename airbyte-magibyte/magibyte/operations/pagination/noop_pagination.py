from .base_pagination import BasePagination


class NoopPagination(BasePagination):
    def __init__(self, **kwargs):
        super(NoopPagination, self).__init__(**kwargs)

    def iterate(self, context):
        pass
