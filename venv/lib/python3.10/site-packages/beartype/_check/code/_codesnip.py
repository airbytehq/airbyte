#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator **type-checking expression snippets** (i.e., triple-quoted
pure-Python string constants formatted and concatenated together to dynamically
generate boolean expressions type-checking arbitrary objects against arbitrary
PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.checkmagic import (
    VAR_NAME_RANDOM_INT,
)

# ....................{ PITH                               }....................
PEP_CODE_PITH_ASSIGN_EXPR = '''{pith_curr_var_name} := {pith_curr_expr}'''
'''
Python >= 3.8-specific assignment expression assigning the full Python
expression yielding the value of the current pith to a unique local variable,
enabling PEP-compliant child hints to obtain this pith via this efficient
variable rather than via this inefficient full Python expression.
'''

# ....................{ HINT ~ placeholder : child         }....................
PEP_CODE_HINT_CHILD_PLACEHOLDER_PREFIX = '@['
'''
Prefix of each **placeholder hint child type-checking substring** (i.e.,
placeholder to be globally replaced by a Python code snippet type-checking the
current pith expression against the currently iterated child hint of the
currently visited parent hint).
'''


PEP_CODE_HINT_CHILD_PLACEHOLDER_SUFFIX = ')!'
'''
Suffix of each **placeholder hint child type-checking substring** (i.e.,
placeholder to be globally replaced by a Python code snippet type-checking the
current pith expression against the currently iterated child hint of the
currently visited parent hint).
'''

# ....................{ HINT ~ placeholder : forwardref    }....................
PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_PREFIX = '${FORWARDREF:'
'''
Prefix of each **placeholder unqualified forward reference classname
substring** (i.e., placeholder to be globally replaced by a Python code snippet
evaluating to the currently visited unqualified forward reference hint
canonicalized into a fully-qualified classname relative to the external
caller-defined module declaring the currently decorated callable).
'''


PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_SUFFIX = ']?'
'''
Suffix of each **placeholder unqualified forward reference classname
substring** (i.e., placeholder to be globally replaced by a Python code snippet
evaluating to the currently visited unqualified forward reference hint
canonicalized into a fully-qualified classname relative to the external
caller-defined module declaring the currently decorated callable).
'''

# ....................{ HINT ~ pep : (484|585) : generic   }....................
PEP484585_CODE_HINT_GENERIC_PREFIX = '''(
{indent_curr}    # True only if this pith is of this generic type.
{indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and'''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
against each unerased pseudo-superclass subclassed by a :pep:`484`-compliant
**generic** (i.e., PEP-compliant type hint subclassing a combination of one or
more of the :mod:`typing.Generic` superclass, the :mod:`typing.Protocol`
superclass, and/or other :mod:`typing` non-class objects).

Caveats
----------
The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent type has been generated.
'''


PEP484585_CODE_HINT_GENERIC_SUFFIX = '''
{indent_curr})'''
'''
PEP-compliant code snippet suffixing all code type-checking the current pith
against each unerased pseudo-superclass subclassed by a :pep:`484`-compliant
generic.
'''


PEP484585_CODE_HINT_GENERIC_CHILD = '''
{{indent_curr}}    # True only if this pith deeply satisfies this unerased
{{indent_curr}}    # pseudo-superclass of this generic.
{{indent_curr}}    {hint_child_placeholder} and'''
'''
PEP-compliant code snippet type-checking the current pith against the current
unerased pseudo-superclass subclassed by a :pep:`484`-compliant generic.

Caveats
----------
The caller is required to manually slice the trailing suffix ``" and"`` after
applying this snippet to the last unerased pseudo-superclass of such a generic.
While there exist alternate and more readable means of accomplishing this, this
approach is the optimally efficient.

The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent type has been generated.
'''

# ....................{ HINT ~ pep : (484|585) : sequence  }....................
PEP484585_CODE_HINT_SEQUENCE_ARGS_1 = '''(
{indent_curr}    # True only if this pith is of this sequence type.
{indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and
{indent_curr}    # True only if either this pith is empty *OR* this pith is
{indent_curr}    # both non-empty and a random item deeply satisfies this hint.
{indent_curr}    (not {pith_curr_var_name} or {hint_child_placeholder})
{indent_curr})'''
'''
PEP-compliant code snippet type-checking the current pith against a parent
**standard sequence type** (i.e., PEP-compliant type hint accepting exactly one
subscripted type hint unconditionally constraining *all* items of this pith,
which necessarily satisfies the :class:`collections.abc.Sequence` protocol with
guaranteed ``O(1)`` indexation across all sequence items).

Caveats
----------
**This snippet cannot contain ternary conditionals.** For unknown reasons
suggesting a critical defect in the current implementation of Python 3.8's
assignment expressions, this snippet raises :class:`UnboundLocalError`
exceptions resembling the following when this snippet contains one or more
ternary conditionals:

    UnboundLocalError: local variable '__beartype_pith_1' referenced before assignment

In particular, the initial draft of this snippet guarded against empty
sequences with a seemingly reasonable ternary conditional:

.. code-block:: python

   PEP484585_CODE_HINT_SEQUENCE_ARGS_1 = \'\'\'(
   {indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and
   {indent_curr}    {hint_child_placeholder} if {pith_curr_var_name} else True
   {indent_curr})\'\'\'

That should behave as expected, but doesn't, presumably due to obscure scoping
rules and a non-intuitive implementation of ternary conditionals in CPython.
Ergo, the current version of this snippet guards against empty sequences with
disjunctions and conjunctions (i.e., ``or`` and ``and`` operators) instead.
Happily, the current version is more efficient than the equivalent approach
based on ternary conditional (albeit slightly less intuitive).
'''


PEP484585_CODE_HINT_SEQUENCE_ARGS_1_PITH_CHILD_EXPR = (
    f'''{{pith_curr_var_name}}[{VAR_NAME_RANDOM_INT} % len({{pith_curr_var_name}})]''')
'''
PEP-compliant Python expression yielding the value of a randomly indexed item
of the current pith (which, by definition, *must* be a standard sequence).
'''

# ....................{ HINT ~ pep : (484|585) : tuple     }....................
PEP484585_CODE_HINT_TUPLE_FIXED_PREFIX = '''(
{indent_curr}    # True only if this pith is a tuple.
{indent_curr}    isinstance({pith_curr_assign_expr}, tuple) and'''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
against each subscripted child hint of an itemized :class:`typing.Tuple` type
of the form ``typing.Tuple[{typename1}, {typename2}, ..., {typenameN}]``.
'''


PEP484585_CODE_HINT_TUPLE_FIXED_SUFFIX = '''
{indent_curr})'''
'''
PEP-compliant code snippet suffixing all code type-checking the current pith
against each subscripted child hint of an itemized :class:`typing.Tuple` type
of the form ``typing.Tuple[{typename1}, {typename2}, ..., {typenameN}]``.
'''


PEP484585_CODE_HINT_TUPLE_FIXED_EMPTY = '''
{{indent_curr}}    # True only if this tuple is empty.
{{indent_curr}}    not {pith_curr_var_name} and'''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
to be empty against an itemized :class:`typing.Tuple` type of the non-standard
form ``typing.Tuple[()]``.

See Also
----------
:data:`PEP484585_CODE_HINT_TUPLE_FIXED_NONEMPTY_CHILD`
    Further details.
'''


PEP484585_CODE_HINT_TUPLE_FIXED_LEN = '''
{{indent_curr}}    # True only if this tuple is of the expected length.
{{indent_curr}}    len({pith_curr_var_name}) == {hint_childs_len} and'''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
to be of the expected length against an itemized :class:`typing.Tuple` type of
the non-standard form ``typing.Tuple[()]``.

See Also
----------
:data:`PEP484585_CODE_HINT_TUPLE_FIXED_NONEMPTY_CHILD`
    Further details.
'''


PEP484585_CODE_HINT_TUPLE_FIXED_NONEMPTY_CHILD = '''
{{indent_curr}}    # True only if this item of this non-empty tuple deeply
{{indent_curr}}    # satisfies this child hint.
{{indent_curr}}    {hint_child_placeholder} and'''
'''
PEP-compliant code snippet type-checking the current pith against the current
child hint subscripting an itemized :class:`typing.Tuple` type of the form
``typing.Tuple[{typename1}, {typename2}, ..., {typenameN}]``.

Caveats
----------
The caller is required to manually slice the trailing suffix ``" and"`` after
applying this snippet to the last subscripted child hint of an itemized
:class:`typing.Tuple` type. While there exist alternate and more readable means
of accomplishing this, this approach is the optimally efficient.

The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent type has been generated.
'''


PEP484585_CODE_HINT_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR = (
    '''{pith_curr_var_name}[{pith_child_index}]''')
'''
PEP-compliant Python expression yielding the value of the currently indexed
item of the current pith (which, by definition, *must* be a tuple).
'''

# ....................{ HINT ~ pep : (484|585) : subclass  }....................
PEP484585_CODE_HINT_SUBCLASS = '''(
{indent_curr}    # True only if this pith is a class *AND*...
{indent_curr}    isinstance({pith_curr_assign_expr}, type) and
{indent_curr}    # True only if this class subclasses this superclass.
{indent_curr}    issubclass({pith_curr_var_name}, {hint_curr_expr})
{indent_curr})'''
'''
PEP-compliant code snippet type-checking the current pith to be a subclass of
the subscripted child hint of a :pep:`484`- or :pep:`585`-compliant **subclass
type hint** (e.g., :attr:`typing.Type`, :class:`type`).
'''

# ....................{ HINT ~ pep : 484 : instance        }....................
PEP484_CODE_HINT_INSTANCE = (
    '''isinstance({pith_curr_expr}, {hint_curr_expr})''')
'''
PEP-compliant code snippet type-checking the current pith against the
current child PEP-compliant type expected to be a trivial non-:mod:`typing`
type (e.g., :class:`int`, :class:`str`).
'''

# ....................{ HINT ~ pep : 484 : union           }....................
PEP484_CODE_HINT_UNION_PREFIX = '''('''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
against each subscripted argument of a :class:`typing.Union` type hint.
'''


PEP484_CODE_HINT_UNION_SUFFIX = '''
{indent_curr})'''
'''
PEP-compliant code snippet suffixing all code type-checking the current pith
against each subscripted argument of a :class:`typing.Union` type hint.
'''


PEP484_CODE_HINT_UNION_CHILD_PEP = '''
{{indent_curr}}    {hint_child_placeholder} or'''
'''
PEP-compliant code snippet type-checking the current pith against the current
PEP-compliant child argument subscripting a parent :class:`typing.Union` type
hint.

Caveats
----------
The caller is required to manually slice the trailing suffix ``" or"`` after
applying this snippet to the last subscripted argument of such a hint. While
there exist alternate and more readable means of accomplishing this, this
approach is the optimally efficient.

The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent hint has been generated.
'''


PEP484_CODE_HINT_UNION_CHILD_NONPEP = '''
{{indent_curr}}    # True only if this pith is of one of these types.
{{indent_curr}}    isinstance({pith_curr_expr}, {hint_curr_expr}) or'''
'''
PEP-compliant code snippet type-checking the current pith against the current
PEP-noncompliant child argument subscripting a parent :class:`typing.Union`
type hint.

See Also
----------
:data:`PEP484_CODE_HINT_UNION_CHILD_PEP`
    Further details.
'''

# ....................{ HINT ~ pep : 586                   }....................
PEP586_CODE_HINT_PREFIX = '''(
{{indent_curr}}    # True only if this pith is of one of these literal types.
{{indent_curr}}    isinstance({pith_curr_assign_expr}, {hint_child_types_expr}) and ('''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
against a :pep:`586`-compliant :class:`typing.Literal` type hint subscripted by
one or more literal objects.
'''


PEP586_CODE_HINT_SUFFIX = '''
{indent_curr}))'''
'''
PEP-compliant code snippet suffixing all code type-checking the current pith
against a :pep:`586`-compliant :class:`typing.Literal` type hint subscripted by
one or more literal objects.
'''


PEP586_CODE_HINT_LITERAL = '''
{{indent_curr}}        # True only if this pith is equal to this literal.
{{indent_curr}}        {pith_curr_var_name} == {hint_child_expr} or'''
'''
PEP-compliant code snippet type-checking the current pith against the current
child literal object subscripting a :pep:`586`-compliant
:class:`typing.Literal` type hint.

Caveats
----------
The caller is required to manually slice the trailing suffix ``" and"`` after
applying this snippet to the last subscripted argument of such a
:class:`typing.Literal` type. While there exist alternate and more readable
means of accomplishing this, this approach is the optimally efficient.

The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent hint has been generated.
'''

# ....................{ HINT ~ pep : 593                   }....................
PEP593_CODE_HINT_VALIDATOR_PREFIX = '''(
{indent_curr}    {hint_child_placeholder} and'''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
against a :pep:`593`-compliant :class:`typing.Annotated` type hint subscripted
by one or more :class:`beartype.vale.BeartypeValidator` objects.
'''


PEP593_CODE_HINT_VALIDATOR_SUFFIX = '''
{indent_curr})'''
'''
PEP-compliant code snippet suffixing all code type-checking the current pith
against each a :pep:`593`-compliant :class:`typing.Annotated` type hint
subscripted by one or more :class:`beartype.vale.BeartypeValidator` objects.
'''


PEP593_CODE_HINT_VALIDATOR_CHILD = '''
{indent_curr}    # True only if this pith satisfies this caller-defined
{indent_curr}    # validator of this annotated.
{indent_curr}    {hint_child_expr} and'''
'''
PEP-compliant code snippet type-checking the current pith against
:mod:`beartype`-specific **data validator code** (i.e., caller-defined
:meth:`beartype.vale.BeartypeValidator._is_valid_code` string) of the current
child :class:`beartype.vale.BeartypeValidator` argument subscripting a parent `PEP
593`_-compliant :class:`typing.Annotated` type hint.

Caveats
----------
The caller is required to manually slice the trailing suffix ``" and"`` after
applying this snippet to the last subscripted argument of such a
:class:`typing.Annotated` type. While there exist alternate and more readable
means of accomplishing this, this approach is the optimally efficient.
'''
