from magibyte.strategies.base_operation import BaseOperation


class BaseDecode(BaseOperation):
    def decode(self, context):
        """
        Decode the body of the response.

        :param context: the current execution context
        :return: a json representing the output
        """
        raise NotImplementedError()
