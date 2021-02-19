import jmespath

from magibyte.strategies.base_operation import BaseOperation


class SeekPaginator(BaseOperation):

    def paginate(self, context):
        decoded_data = context['decoded_response']

        value_extractor = self.extrapolate(self.options.get('value'), context)

        # The output of the query should be a scalar
        value = jmespath.search(value_extractor, decoded_data)
        if type(value) not in (str, int):
            raise ValueError()

        return {value}
