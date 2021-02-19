from magibyte.strategies.base_operation import BaseOperation


class BaseRequest(BaseOperation):

    def request(self, context):
        raise NotImplementedError()
