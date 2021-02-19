import jmespath

from magibyte.strategies.base_operation import BaseOperation


class NoopPaginator(BaseOperation):

    def paginate(self, context):
        yield None
