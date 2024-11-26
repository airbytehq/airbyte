#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype exception and warning hierarchies.**

This submodule publishes a hierarchy of:

* :mod:`beartype`-specific exceptions raised both by:

  * The :func:`beartype.beartype` decorator at decoration and call time.
  * Other public submodules and subpackages at usage time, including
    user-defined data validators imported from the :mod:`beartype.vale`
    subpackage.

* :mod:`beartype`-specific warnings emitted at similar times.

Hear :mod:`beartype` roar as it efficiently checks types, validates data, and
raids native beehives for organic honey.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To prevent "mypy --no-implicit-reexport" from raising literally
# hundreds of errors at static analysis time, *ALL* public attributes *MUST* be
# explicitly reimported under the same names with "{exception_name} as
# {exception_name}" syntax rather than merely "{exception_name}". Yes, this is
# ludicrous. Yes, this is mypy. For posterity, these failures resemble:
#     beartype/_cave/_cavefast.py:47: error: Module "beartype.roar" does not
#     explicitly export attribute "BeartypeCallUnavailableTypeException";
#     implicit reexport disabled  [attr-defined]
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Public exception hierarchy.
from beartype.roar._roarexc import (
    # Exceptions.
    BeartypeException as BeartypeException,
    BeartypeCaveException as BeartypeCaveException,
    BeartypeCaveNoneTypeOrException as BeartypeCaveNoneTypeOrException,
    BeartypeCaveNoneTypeOrKeyException as BeartypeCaveNoneTypeOrKeyException,
    BeartypeCaveNoneTypeOrMutabilityException as BeartypeCaveNoneTypeOrMutabilityException,
    BeartypeClawException as BeartypeClawException,
    BeartypeClawHookException as BeartypeClawHookException,
    BeartypeClawImportException as BeartypeClawImportException,
    BeartypeClawImportAstException as BeartypeClawImportAstException,
    BeartypeClawImportConfException as BeartypeClawImportConfException,
    BeartypeConfException as BeartypeConfException,
    BeartypeConfParamException as BeartypeConfParamException,
    BeartypeConfShellVarException as BeartypeConfShellVarException,
    BeartypeDoorException as BeartypeDoorException,
    BeartypeDoorNonpepException as BeartypeDoorNonpepException,
    BeartypeDoorPepException as BeartypeDoorPepException,
    BeartypeDoorPepUnsupportedException as BeartypeDoorPepUnsupportedException,
    BeartypeDecorException as BeartypeDecorException,
    BeartypeDecorWrappeeException as BeartypeDecorWrappeeException,
    BeartypeDecorWrapperException as BeartypeDecorWrapperException,
    BeartypeDecorHintException as BeartypeDecorHintException,
    BeartypeDecorHintForwardRefException as BeartypeDecorHintForwardRefException,
    BeartypeDecorHintNonpepException as BeartypeDecorHintNonpepException,
    BeartypeDecorHintNonpepNumpyException as BeartypeDecorHintNonpepNumpyException,
    BeartypeDecorHintNonpepPanderaException as BeartypeDecorHintNonpepPanderaException,
    BeartypeDecorHintPepException as BeartypeDecorHintPepException,
    BeartypeDecorHintPepSignException as BeartypeDecorHintPepSignException,
    BeartypeDecorHintPepUnsupportedException as BeartypeDecorHintPepUnsupportedException,
    BeartypeDecorHintPep484Exception as BeartypeDecorHintPep484Exception,
    BeartypeDecorHintPep484585Exception as BeartypeDecorHintPep484585Exception,
    BeartypeDecorHintPep544Exception as BeartypeDecorHintPep544Exception,
    BeartypeDecorHintPep557Exception as BeartypeDecorHintPep557Exception,
    BeartypeDecorHintPep585Exception as BeartypeDecorHintPep585Exception,
    BeartypeDecorHintPep586Exception as BeartypeDecorHintPep586Exception,
    BeartypeDecorHintPep591Exception as BeartypeDecorHintPep591Exception,
    BeartypeDecorHintPep593Exception as BeartypeDecorHintPep593Exception,
    BeartypeDecorHintPep647Exception as BeartypeDecorHintPep647Exception,
    BeartypeDecorHintPep673Exception as BeartypeDecorHintPep673Exception,
    BeartypeDecorHintPep3119Exception as BeartypeDecorHintPep3119Exception,
    BeartypeDecorHintTypeException as BeartypeDecorHintTypeException,
    BeartypeDecorParamException as BeartypeDecorParamException,
    BeartypeDecorParamNameException as BeartypeDecorParamNameException,
    BeartypeCallException as BeartypeCallException,
    BeartypeCallUnavailableTypeException as BeartypeCallUnavailableTypeException,
    BeartypeCallHintException as BeartypeCallHintException,
    BeartypeCallHintForwardRefException as BeartypeCallHintForwardRefException,
    BeartypePepException as BeartypePepException,
    BeartypePep563Exception as BeartypePep563Exception,
    BeartypeValeException as BeartypeValeException,
    BeartypeValeSubscriptionException as BeartypeValeSubscriptionException,
    BeartypeValeValidationException as BeartypeValeValidationException,

    # Violations (i.e., exceptions raised during runtime type-checking).
    BeartypeCallHintViolation as BeartypeCallHintViolation,
    BeartypeCallHintParamViolation as BeartypeCallHintParamViolation,
    BeartypeCallHintReturnViolation as BeartypeCallHintReturnViolation,
    BeartypeDoorHintViolation as BeartypeDoorHintViolation,
)

# Public warning hierarchy.
from beartype.roar._roarwarn import (
    BeartypeWarning as BeartypeWarning,
    BeartypeClawWarning as BeartypeClawWarning,
    BeartypeClawDecorWarning as BeartypeClawDecorWarning,
    BeartypeConfWarning as BeartypeConfWarning,
    BeartypeConfShellVarWarning as BeartypeConfShellVarWarning,
    BeartypeDecorHintWarning as BeartypeDecorHintWarning,
    # BeartypeDecorHintForwardRefWarning as BeartypeDecorHintForwardRefWarning,
    BeartypeDecorHintPepWarning as BeartypeDecorHintPepWarning,
    BeartypeDecorHintPepDeprecationWarning as BeartypeDecorHintPepDeprecationWarning,
    BeartypeDecorHintPep585DeprecationWarning as BeartypeDecorHintPep585DeprecationWarning,
    BeartypeDecorHintNonpepWarning as BeartypeDecorHintNonpepWarning,
    BeartypeDecorHintNonpepNumpyWarning as BeartypeDecorHintNonpepNumpyWarning,
    BeartypeModuleWarning as BeartypeModuleWarning,
    BeartypeModuleNotFoundWarning as BeartypeModuleNotFoundWarning,
    BeartypeModuleAttributeNotFoundWarning as BeartypeModuleAttributeNotFoundWarning,
    BeartypeModuleUnimportableWarning as BeartypeModuleUnimportableWarning,
    BeartypeValeWarning as BeartypeValeWarning,
    BeartypeValeLambdaWarning as BeartypeValeLambdaWarning,
)

# ....................{ DEPRECATIONS                       }....................
def __getattr__(attr_deprecated_name: str) -> object:
    '''
    Dynamically retrieve a deprecated attribute with the passed unqualified
    name from this submodule and emit a non-fatal deprecation warning on each
    such retrieval if this submodule defines this attribute *or* raise an
    exception otherwise.

    The Python interpreter implicitly calls this :pep:`562`-compliant module
    dunder function under Python >= 3.7 *after* failing to directly retrieve an
    explicit attribute with this name from this submodule. Since this dunder
    function is only called in the event of an error, neither space nor time
    efficiency are a concern here.

    Parameters
    ----------
    attr_deprecated_name : str
        Unqualified name of the deprecated attribute to be retrieved.

    Returns
    ----------
    object
        Value of this deprecated attribute.

    Warns
    ----------
    :class:`DeprecationWarning`
        If this attribute is deprecated.

    Raises
    ----------
    :exc:`AttributeError`
        If this attribute is unrecognized and thus erroneous.
    '''

    # Isolate imports to avoid polluting the module namespace.
    from beartype._util.module.utilmoddeprecate import deprecate_module_attr

    # Return the value of this deprecated attribute and emit a warning.
    return deprecate_module_attr(
        attr_deprecated_name=attr_deprecated_name,
        attr_deprecated_name_to_nondeprecated_name={
            'BeartypeAbbyException': (
                'BeartypeDoorException'),
            'BeartypeAbbyHintViolation': (
                'BeartypeDoorHintViolation'),
            'BeartypeAbbyTesterException': (
                'BeartypeDoorException'),
            'BeartypeCallHintPepException': (
                'BeartypeCallHintViolation'),
            'BeartypeCallHintPepParamException': (
                'BeartypeCallHintParamViolation'),
            'BeartypeCallHintPepReturnException': (
                'BeartypeCallHintReturnViolation'),
            'BeartypeDecorHintNonPepException': (
                'BeartypeDecorHintNonpepException'),
            'BeartypeDecorHintNonPepNumPyException': (
                'BeartypeDecorHintNonpepNumpyException'),
            'BeartypeDecorHintPep563Exception': (
                'BeartypePep563Exception'),
            'BeartypeDecorHintPepDeprecatedWarning': (
                'BeartypeDecorHintPepDeprecationWarning'),
            'BeartypeDecorPepException': (
                'BeartypePepException'),
        },
        attr_nondeprecated_name_to_value=globals(),
    )
