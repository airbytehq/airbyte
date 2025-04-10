import numpy as np
from sqlalchemy.dialects.postgresql.base import ischema_names
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import UserDefinedType, Float, String

# this is for airbyte's column definition
class VECTOR(UserDefinedType):
    cache_ok = True
    _string = String()

    def __init__(self, dim=None):
        super(UserDefinedType, self).__init__()
        self.dim = dim

    def get_col_spec(self, **kw):
        if self.dim is None:
            return 'VECTOR'
        return 'VECTOR(%d)' % self.dim

    # the "bind_processor" is for converting the value into something which can be used with parameter binding.
    # That is, if there is a placeholder ":vec" in the query, the result of this processor would be the value being bound to "vec"
    # TODO: this should probably return the vector as an "32-bit IEEE 754 floating point number"
    # see: https://mariadb.com/kb/en/vector-overview/
    # maybe like this? https://stackoverflow.com/questions/59883083/convert-two-raw-values-to-32-bit-ieee-floating-point-number
    def bind_processor(self, dialect):
        def process(value):
            return self._to_db(value)

        return process


    def _to_db(self, value):
        if value is None:
            return value

        if not hasattr(value, "__len__"):
            value = [value]

        if len(value) != self.dim:
            raise ValueError('expected %d dimensions, not %d' % (self.dim, len(value)))

        return '[' + ','.join([str(float(v)) for v in value]) + ']'

    @classmethod
    def _from_db(cls, value):
        if value is None or isinstance(value, np.ndarray):
            return value

        # first, text to array
        as_array = [float(v) for v in value[1:-1].split(',')]

        # then, this array to numpy array?
        if not isinstance(as_array, np.ndarray) or as_array.dtype != '>f4':
            as_array = np.asarray(value, dtype='>f4')

        # finally, whatever this does
        return as_array.astype(np.float32)

    # The "literal_processor" should return a string, which can be inserted into a query as-is.
    # As opposed to when binding is being used.
    def literal_processor(self, dialect):
        # stolen from String
        def process(value):
            value = self._to_db(value)
            value = value.replace("'", "''")

            if dialect.identifier_preparer._double_percents:
                value = value.replace("%", "%%")

            return "'%s'" % value

        return process

    # The "result_processor" is for taking a result, as it comes from the DB, and returning a python variable representing it
    def result_processor(self, dialect, coltype):
        def process(value):
            return self._from_db(value)
        return process

    class ComparatorFactory(TypeEngine.Comparator):
        # stolen from pgvector, I don't know if these are correct...
        def l2_distance(self, other):
            return self.op('<->', return_type=Float)(other)

        def max_inner_product(self, other):
            return self.op('<#>', return_type=Float)(other)

        def cosine_distance(self, other):
            return self.op('<=>', return_type=Float)(other)

        def l1_distance(self, other):
            return self.op('<+>', return_type=Float)(other)

    comparator_factory = ComparatorFactory


# for reflection.. what does this mean? But might be important for the whole SQL generation stuff
ischema_names['vector'] = VECTOR
