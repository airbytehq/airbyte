from magibyte.strategies.base_operation import BaseOperation


class BaseIterator(BaseOperation):

    def iterate(self, context):
        raise NotImplementedError()
