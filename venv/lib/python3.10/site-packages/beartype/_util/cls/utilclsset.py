#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class setters** (i.e., low-level callables modifying various
properties of arbitrary classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10

# ....................{ SETTERS                            }....................
#FIXME: Unit test us up.
def set_type_attr(cls: type, attr_name: str, attr_value: object) -> None:
    '''
    Dynamically set the **class variable** (i.e., attribute of the passed class)
    with the passed name to the passed value.

    Parameters
    ----------
    cls : type
        Class to set this attribute on.
    attr_name : str
        Name of the class attribute to be set.
    attr_value : object
        Value to set this class attribute to.

    Caveats
    -------
    **This function is unavoidably slow.** Class attributes are *only* settable
    by calling the tragically slow :func:`setattr` builtin. Attempting to
    directly set an attribute on the class dictionary raises an exception. Why?
    Because class dictionaries are actually low-level :class:`mappingproxy`
    objects that intentionally override the ``__setattr__()`` dunder method to
    unconditionally raise an exception. Why? Because that constraint enables the
    :meth:`type.__setattr__` dunder method to enforce critical efficiency
    constraints on class attributes -- including that class attribute keys are
    *not* only strings but also valid Python identifiers:

    .. code-block:: pycon

       >>> class OhGodHelpUs(object): pass
       >>> OhGodHelpUs.__dict__['even_god_cannot_help'] = 2
       TypeError: 'mappingproxy' object does not support item
       assignment

    See also this `relevant StackOverflow answer by Python luminary
    Raymond Hettinger <answer_>`__.

    .. _answer:
       https://stackoverflow.com/a/32720603/2809027
    '''

    # Attempt to set the class attribute with this name to this value.
    try:
        setattr(cls, attr_name, attr_value)
    # If doing so raises a builtin "TypeError"...
    except TypeError as exception:
        # Message raised with this "TypeError".
        exception_message = str(exception)

        # If this message satisfies a well-known pattern unique to the current
        # Python version, then this exception signifies this attribute to be
        # inherited from an immutable builtin type (e.g., "str") subclassed by
        # this user-defined subclass. In this case, silently skip past this
        # uncheckable attribute to the next.
        if (
            # The active Python interpreter targets Python >= 3.10, match a
            # message of the form "cannot set '{attr_name}' attribute of
            # immutable type '{cls_name}'".
            IS_PYTHON_AT_LEAST_3_10 and (
                exception_message.startswith("cannot set '") and
                "' attribute of immutable type " in exception_message
            # Else, the active Python interpreter targets Python <= 3.9. In this
            # case, match a message of the form "can't set attributes of
            # built-in/extension type '{cls_name}'".
            ) or exception_message.startswith(
                "can't set attributes of built-in/extension type '")
        ):
            return
        # Else, this message does *NOT* satisfy that pattern.

        # Preserve this exception by re-raising this exception.
        raise
