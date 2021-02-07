from .base_pagination import BasePagination


class SinglePagination(BasePagination):
    def __init__(self, options):
        super(SinglePagination, self).__init__(options)

    def __iter__(self):
        return iter(({}, ))
