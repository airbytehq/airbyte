from magibyte.operations.base_operation import BaseOperation


class BaseSelect(BaseOperation):
    def select(self, context):
        raise NotImplementedError()
