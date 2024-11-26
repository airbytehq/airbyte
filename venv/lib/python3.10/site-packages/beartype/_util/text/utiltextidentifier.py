#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python identifier utilities** (i.e., low-level callables handling
unqualified and qualified attribute, callable, class, module, and variable
names).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilTextIdentifierException
from beartype._data.hint.datahinttyping import TypeException

# ....................{ RAISERS                            }....................
def die_unless_identifier(
    # Mandatory parameters.
    text: str,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilTextIdentifierException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed string is a valid **Python attribute
    name** (i.e., ``.``-delimited concatenation of one or more
    :pep:`3131`-compliant syntactically valid Python identifiers, including the
    names of attributes, callables, classes, modules, and variables).

    Parameters
    ----------
    text : str
        String to be validated.
    exception_cls : Type[Exception]
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilTextIdentifierException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this string in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    exception_cls
        If this string is *not* a valid Python attribute name.

    See Also
    ----------
    :func:`.is_identifier`
        Further details.
    '''

    # If this string is *NOT* a valid Python attribute name, raise an exception.
    if not is_identifier(text):
        assert isinstance(exception_cls, type), (
            'f{repr(exception_cls)} not exception class.')
        assert isinstance(exception_prefix, str), (
            'f{repr(exception_prefix)} not string.')

        raise exception_cls(
            f'{exception_prefix}{repr(text)} not valid Python attribute name.')
    # Else, this string is a valid Python attribute name.

# ....................{ TESTERS                            }....................
def is_identifier(text: str) -> bool:
    '''
    :data:`True` only if the passed string is a valid **Python attribute name**
    (i.e., ``.``-delimited concatenation of one or more :pep:`3131`-compliant
    syntactically valid Python identifiers, including the names of attributes,
    callables, classes, modules, and variables).

    This tester is suitable for detecting whether this string is the
    fully-qualified name of an arbitrary Python object.

    Caveats
    ----------
    **This tester is mildly slow,** due to unavoidably splitting this string on
    ``.`` delimiters and iteratively passing each of the split substrings to
    the :meth:`str.isidentifier` builtin. Due to the following caveat, this
    inefficiency is unavoidable.

    **This tester is not optimizable with regular expressions** -- at least,
    not trivially. Technically, this tester *can* be optimized by leveraging
    the "General Category" of Unicode filters provided by the third-party
    :mod:`regex` package. Practically, doing so would require the third-party
    :mod:`regex` package and would still almost certainly fail in edge cases.
    Why? Because Python 3 permits Python identifiers to contain Unicode letters
    and digits in the "General Category" of Unicode code points, which is
    extremely non-trivial to match with the standard :mod:`re` module.

    Parameters
    ----------
    text : str
        String to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if this string is the ``.``-delimited concatenation of
        one or more syntactically valid Python identifiers.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # If this text contains *NO* "." delimiters and is thus expected to be an
    # unqualified Python identifier, return true only if this is the case.
    if '.' not in text:
        return text.isidentifier()
    # Else, this text contains one or more "." delimiters and is thus expected
    # to be a qualified Python identifier.

    # Return true only if *ALL* "."-delimited substrings split from this string
    # are valid unqualified Python identifiers. Note that:
    # * Regular expressions report false negatives. See the docstring.
    # * Manual iteration is significantly faster than "all(...)"- and
    #   "any(...)"-style comprehensions.
    # * This approach correctly handles *ALL* edge cases, including when:
    #   * This string is simply the "." character. In this case:
    #         >>> '.'.split('.')
    #         ['', '']
    #     Since the empty string is *NOT* a valid Python identifier, this
    #     iteration immediately returns false as expected.
    # * There exists an alternative and significantly more computationally
    #   expensive means of testing this condition, employed by the
    #   typing.ForwardRef.__init__() method to valid the validity of the passed
    #   relative classname:
    #       # Needless to say, we'll never be doing this.
    #       try:
    #           all(
    #               compile(identifier, '<string>', 'eval')
    #               for identifier in text.split('.')
    #           )
    #           return True
    #       except SyntaxError:
    #           return False
    for text_basename in text.split('.'):
        # If this "."-delimited substring is *NOT* a valid unqualified Python
        # identifier, return false.
        if not text_basename.isidentifier():
            return False
        # Else, this "."-delimited substring is a valid unqualified Python
        # identifier. In this case, silently continue to the next.

    # Return true, since *ALL* "."-delimited substrings split from this string
    # are valid unqualified Python identifiers.
    return True
