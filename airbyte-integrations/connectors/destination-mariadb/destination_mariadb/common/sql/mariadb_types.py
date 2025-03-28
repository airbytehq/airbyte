# Mostly stolen from sqlalchemy's pgvector...
import numpy as np
from sqlalchemy.dialects.postgresql.base import ischema_names
from sqlalchemy.types import UserDefinedType, Float, String
# from ..utils import Vector

class VARCHAR(UserDefinedType):
    pass

# this is for airbyte's column definition
# this doesn't event need to be PGVector or MariaDB specific...
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

    # this seems to return a function to convert this column's value (an array) to a string
    # """Return a conversion function for processing bind values.
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

    # this should take a value as string, and return it in proper array format
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

    def literal_processor(self, dialect):
        string_literal_processor = self._string._cached_literal_processor(dialect)

        def process(value):
            return string_literal_processor(self._to_db(value))
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return self._from_db(value)
        return process

    class comparator_factory(UserDefinedType.Comparator):
        def l2_distance(self, other):
            return self.op('<->', return_type=Float)(other)

        def max_inner_product(self, other):
            return self.op('<#>', return_type=Float)(other)

        def cosine_distance(self, other):
            return self.op('<=>', return_type=Float)(other)

        def l1_distance(self, other):
            return self.op('<+>', return_type=Float)(other)


# for reflection.. what does this mean? But might be important for the whole SQL generation stuff
ischema_names['vector'] = VECTOR
