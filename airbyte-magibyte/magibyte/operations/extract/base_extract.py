from magibyte.operations.base_operation import BaseOperation


class BaseExtract(BaseOperation):

    def extract(self, context):
        raise NotImplementedError()
