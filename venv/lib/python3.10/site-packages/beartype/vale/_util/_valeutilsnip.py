#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype validator code snippets** (i.e., triple-quoted pure-Python code
constants formatted and concatenated together into wrapper functions
type-checking decorated callables annotated by one or more beartype
validators).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.text.utiltextmagic import CODE_INDENT_1

# ....................{ INDENTATION                        }....................
VALE_CODE_INDENT_1 = f'{{indent}}{CODE_INDENT_1}'
'''
Code snippet prefixed by the placeholder substring ``"{indent}"`` (which the
:func:`beartype._check.code.codemake.make_func_wrapper_code` replaces with
the indentation level required by the current beartype validator) followed by a
single level of indentation.
'''

# ....................{ CHECK ~ factory                    }....................
VALE_CODE_CHECK_ISEQUAL_TEST = '''
{{indent}}# True only if this pith equals this object.
{{indent}}{{obj}} == {param_name_obj_value}'''
'''
:attr:`beartype.vale.IsEqual`-specific code snippet validating an arbitrary
object to be equal to another arbitrary object.
'''


VALE_CODE_CHECK_ISINSTANCE_TEST = '''
{{indent}}# True only if this pith is an object instancing this superclass.
{{indent}}isinstance({{obj}}, {param_name_types})'''
'''
:attr:`beartype.vale.IsInstance`-specific code snippet validating an arbitrary
object to instance an arbitrary type.
'''


VALE_CODE_CHECK_ISSUBCLASS_TEST = '''
{{indent}}# True only if this pith is a class subclassing this superclass.
{{indent}}(isinstance({{obj}}, type) and issubclass({{obj}}, {param_name_types}))'''
'''
:attr:`beartype.vale.IsSubclass`-specific code snippet validating an arbitrary
type to subclass another arbitrary type.
'''

# ....................{ CHECK ~ factory : isattr           }....................
VALE_CODE_CHECK_ISATTR_TEST = '''(
{{indent}}    # True only if this pith defines an attribute with this name.
{{indent}}    {attr_value_expr}
{{indent}}    is not {local_name_sentinel} and {attr_value_is_valid_expr}
{{indent}})'''
'''
:attr:`beartype.vale.IsAttr`-specific code snippet validating an arbitrary
object to define an attribute with an arbitrary name satisfying an arbitrary
expression evaluating to a boolean.
'''


_VALE_CODE_CHECK_ISATTR_VALUE_EXPR_RAW = (
    'getattr({{obj}}, {attr_name_expr}, {local_name_sentinel})')
'''
:attr:`beartype.vale.IsAttr`-specific Python expression inefficiently yielding
the value of the attribute with an arbitrary name of an arbitrary object to be
validated.
'''


VALE_CODE_CHECK_ISATTR_VALUE_EXPR = (
    f'({{local_name_attr_value}} := {_VALE_CODE_CHECK_ISATTR_VALUE_EXPR_RAW})')
'''
:attr:`beartype.vale.IsAttr`-specific Python expression efficiently yielding
the value of the attribute with an arbitrary name of an arbitrary object to be
validated.

For efficiency, this expression is optimized to localize this value to a local
variable whose name *must* be uniquified and formatted by the caller into the
``local_name_attr_value`` format variable.
'''

# ....................{ METHODS                            }....................
# Format methods of the code snippets declared above as a microoptimization.

VALE_CODE_CHECK_ISATTR_TEST_format = VALE_CODE_CHECK_ISATTR_TEST.format
VALE_CODE_CHECK_ISATTR_VALUE_EXPR_format = (
    VALE_CODE_CHECK_ISATTR_VALUE_EXPR.format)
VALE_CODE_CHECK_ISEQUAL_TEST_format = VALE_CODE_CHECK_ISEQUAL_TEST.format
VALE_CODE_CHECK_ISINSTANCE_TEST_format = VALE_CODE_CHECK_ISINSTANCE_TEST.format
VALE_CODE_CHECK_ISSUBCLASS_TEST_format = VALE_CODE_CHECK_ISSUBCLASS_TEST.format
