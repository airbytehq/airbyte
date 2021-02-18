from magibyte.strategies.base_operation import BaseOperation


class BaseSchema(BaseOperation):

    def get(self):
        raise NotImplementedError()
