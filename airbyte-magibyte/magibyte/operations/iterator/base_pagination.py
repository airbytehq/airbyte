from magibyte.operations.base_operation import BaseOperation


class BasePagination(BaseOperation):

    def iterate(self, context):
        raise NotImplementedError()
