import jmespath

from magibyte.strategies.base_operation import BaseOperation


class SeekPaginator(BaseOperation):

    def paginate(self, context):
        while True:
            decoded_data = context.get('decoded_response')
            # for the first page we don't return any value
            if not decoded_data:
                yield {}
            else:
                value_extractor = self.extrapolate(self.options.get('value'), context)

                # The output of the query should be a scalar
                value = jmespath.search(value_extractor, decoded_data)
                if value and type(value) not in (str, int):
                    raise ValueError()

                # if we can't find the seek value, then we stop going through pages
                if not value:
                    break

                yield {'value': value}
