from magibyte.strategies.base_operation import BaseOperation


class BasePaginator(BaseOperation):

    def paginate(self, context):
        raise NotImplementedError()
