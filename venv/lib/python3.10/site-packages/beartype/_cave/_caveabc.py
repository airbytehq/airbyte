#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
:mod:`beartype.cave`-specific **abstract base classes (ABCs).**
'''

# ....................{ TODO                               }....................
#FIXME: Refactor this private submodule into a new public "beartype.caver"
#submodule, so-named as it enables users to externally create new ad-hoc
#protocols implementing structural subtyping resembling those predefined by
#"beartype.cave". To do so:
#
#* In the "beartype.caver" submodule:
#  * Define a new make_type_structural() function with signature resembling:
#    def make_type_structural(name: str, method_names: Iterable) -> type:
#  * Implement this function to dynamically create a new type with the passed
#    classname defining:
#    * Abstract methods with the passed method names.
#    * A __subclasshook__() dunder method checking the passed class for
#      concrete methods with these names.
#    To do so, note that abstract methods *CANNOT* be dynamically
#    monkey-patched in after class creation but *MUST* instead be statically
#    defined at class creation time (due to metaclass shenanigans).
#    Fortunately, doing so is trivial; simply use the three-argument form of
#    the type() constructor, as demonstrated by this StackOverflow answer:
#    https://stackoverflow.com/a/14219244/2809027
#  * *WAIT!* There's no need to call the type() constructor directly. Instead,
#    define a new make_type() function in this new submodule copied from the
#    betse.util.type.classes.define_class() function (but renamed, obviously).
#* Replace the current manual definition of "_BoolType" below with an in-place
#  call to that method from the "beartype.cave" submodule: e.g.,
#    BoolType = _make_type_structural(
#        name='BoolType', method_names=('__bool__',))
#
#Dis goin' be good.
#FIXME: Actually, don't do any of the above. That would simply be reinventing
#the wheel, as the "typing.Protocol" superclass already exists and is more than
#up to the task. In fact, once we drop support for Python < 3.7, we should:
#* Redefine the "_BoolType" class declared below should in terms of the
#  "typing.Protocol" superclass.
#* Shift the "_BoolType" class directly into the "beartype.cave" submodule.
#* Refactor away this entire submodule.

# ....................{ IMPORTS                            }....................
from abc import ABCMeta, abstractmethod

# ....................{ FUNCTIONS                          }....................
def _check_methods(C: type, *methods: str):
    '''
    Private utility function called by abstract base classes (ABCs) implementing
    structural subtyping by detecting whether the passed class or some
    superclass of that class defines all of the methods with the passed method
    names.

    For safety, this function has been duplicated as is from its eponymous
    counterpart in the private stdlib :mod:`_colletions_abc` module.

    Parameters
    ----------
    C : type
        Class to be validated as defining these methods.
    methods : Tuple[str, ...]
        Tuple of the names of all methods to validate this class as defining.

    Returns
    ----------
    Either:

        * ``True`` if this class defines all of these methods.
        * ``NotImplemented`` if this class fails to define one or more of these
          methods.
    '''

    mro = C.__mro__
    for method in methods:
        for B in mro:  # pyright: ignore[reportGeneralTypeIssues]
            if method in B.__dict__:
                if B.__dict__[method] is None:
                    return NotImplemented
                break
        else:
            return NotImplemented

    return True

# ....................{ SUPERCLASSES                       }....................
class BoolType(object, metaclass=ABCMeta):
    '''
    Type of all **booleans** (i.e., objects defining the ``__bool__()`` dunder
    method; objects reducible in boolean contexts like ``if`` conditionals to
    either ``True`` or ``False``).

    This type matches:

    * **Builtin booleans** (i.e., instances of the standard :class:`bool` class
      implemented in low-level C).
    * **NumPy booleans** (i.e., instances of the :class:`numpy.bool_` class
      implemented in low-level C and Fortran) if :mod:`numpy` is importable.

    Usage
    ----------
    Non-standard boolean types like NumPy booleans are typically *not*
    interoperable with the standard standard :class:`bool` type. In particular,
    it is typically *not* the case, for any variable ``my_bool`` of
    non-standard boolean type and truthy value, that either ``my_bool is True``
    or ``my_bool == True`` yield the desired results. Rather, such variables
    should *always* be coerced into the standard :class:`bool` type before
    being compared -- either:

    * Implicitly (e.g., ``if my_bool: pass``).
    * Explicitly (e.g., ``if bool(my_bool): pass``).

    Caveats
    ----------
    **There exists no abstract base class governing booleans in Python.**
    Although various Python Enhancement Proposals (PEPs) were authored on the
    subject, all were rejected as of this writing. Instead, this type trivially
    implements an ad-hoc abstract base class (ABC) detecting objects satisfying
    the boolean protocol via structural subtyping. Although no actual
    real-world classes subclass this :mod:`beartype`-specific ABC, the
    detection implemented by this ABC suffices to match *all* boolean types.

    See Also
    ----------
    :class:`beartype.cave.ContainerType`
        Further details on structural subtyping.
    '''

    # ..................{ DUNDERS                            }..................
    # This abstract base class (ABC) has been implemented ala standard
    # container ABCs in the private stdlib "_collections_abc" module (e.g., the
    # trivial "_collections_abc.Sized" type).
    __slots__ = ()

    @abstractmethod
    def __bool__(self):
        return False

    @classmethod
    def __subclasshook__(cls, C):
        if cls is BoolType:
            return _check_methods(C, '__bool__')
        return NotImplemented
