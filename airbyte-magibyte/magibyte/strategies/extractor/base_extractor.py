from magibyte.strategies.base_operation import BaseOperation


class BaseExtractor(BaseOperation):

    def extract(self, context):
        raise NotImplementedError()
