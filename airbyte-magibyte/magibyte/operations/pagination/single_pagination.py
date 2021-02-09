from .base_pagination import BasePagination


class SinglePagination(BasePagination):
    def __init__(self, **kwargs):
        super(SinglePagination, self).__init__(**kwargs)

    def iterate(self, context):
        yield {}
