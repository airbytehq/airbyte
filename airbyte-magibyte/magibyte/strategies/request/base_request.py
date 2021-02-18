from magibyte.strategies.base_operation import BaseOperation


class BaseRequest(BaseOperation):

    def build(self, context):
        raise NotImplementedError()
