# Mostly stolen from sqlalchemy's pgvector...
import numpy as np
from sqlalchemy.dialects.postgresql.base import ischema_names
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import UserDefinedType, Float, String
# from ..utils import Vector

# this is for airbyte's column definition
# doesn't even need to be PGVector or MariaDB specific, but doesn't seem to exist in shared
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
        # stolen from String
        def process(value):
            value = self._to_db(value)
            value = value.replace("'", "''")

            if dialect.identifier_preparer._double_percents:
                value = value.replace("%", "%%")

            return "'%s'" % value

        return process


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
        """
        # the robot also suggested this, but I don't get it
        def cosine_similarity(self, other):
            return func.cosine_similarity(self.expr, other)
        
        def euclidean_distance(self, other):
            return func.euclidean_distance(self.expr, other)
            
        def dot_product(self, other):
            return func.dot_product(self.expr, other)
            
        def nearest_neighbors(self, other, k=10):
            # Example of a function that might find k nearest neighbors
            return func.nearest_neighbors(self.expr, other, k)
        
        @compiles(func.cosine_similarity)
        def compile_cosine_similarity(element, compiler, **kw):
            return f"COSINE_SIMILARITY({compiler.process(element.clauses.clauses[0])}, {compiler.process(element.clauses.clauses[1])})"
        
        @compiles(func.euclidean_distance)
        def compile_euclidean_distance(element, compiler, **kw):
            return f"EUCLIDEAN_DISTANCE({compiler.process(element.clauses.clauses[0])}, {compiler.process(element.clauses.clauses[1])})"
        
        @compiles(func.dot_product)
        def compile_dot_product(element, compiler, **kw):
            return f"DOT_PRODUCT({compiler.process(element.clauses.clauses[0])}, {compiler.process(element.clauses.clauses[1])})"
        
        @compiles(func.nearest_neighbors)
        def compile_nearest_neighbors(element, compiler, **kw):
            if len(element.clauses.clauses) == 3:
                return f"NEAREST_NEIGHBORS({compiler.process(element.clauses.clauses[0])}, {compiler.process(element.clauses.clauses[1])}, {compiler.process(element.clauses.clauses[2])})"
            else:
                return f"NEAREST_NEIGHBORS({compiler.process(element.clauses.clauses[0])}, {compiler.process(element.clauses.clauses[1])})"
        
        """

    comparator_factory = ComparatorFactory


# for reflection.. what does this mean? But might be important for the whole SQL generation stuff
ischema_names['vector'] = VECTOR
