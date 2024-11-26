#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype fast cave** (i.e., private subset of the public :mod:`beartype.cave`
subpackage profiled to be efficiently importable at :mod:`beartype` startup and
thus safely importable throughout the internal :mod:`beartype` codebase).

The public :mod:`beartype.cave` subpackage has been profiled to *not* be
efficiently importable at :mod:`beartype` startup and thus *not* safely
importable throughout the internal :mod:`beartype` codebase. Why? Because
:mod:`beartype.cave` currently imports from expensive third-party packages on
importation (e.g., :mod:`numpy`) despite :mod:`beartype` itself *never*
requiring those imports. Until resolved, that subpackage is considered tainted.
'''

# ....................{ TODO                               }....................
#FIXME: Add types for all remaining useful "collections.abc" interfaces,
#including:
#* "Reversible".
#* "AsyncIterable".
#* "AsyncIterator".
#* "AsyncGenerator".
#
#There certainly exist other "collections.abc" interfaces as well, but it's
#unclear whether they have any practical real-world utility during type
#checking. These include:
#* "ByteString". (wut)
#* Dictionary-specific views (e.g., "MappingView", "ItemsView").

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import functools as _functools
import numbers as _numbers
import re as _re
from beartype.roar import BeartypeCallUnavailableTypeException
from beartype._cave._caveabc import BoolType
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_9,
)
from collections import deque as _deque
from collections.abc import (
    Collection as _Collection,
    Container as _Container,
    Generator as _Generator,
    Hashable as _Hashable,
    Iterable as _Iterable,
    Iterator as _Iterator,
    Mapping as _Mapping,
    MutableMapping as _MutableMapping,
    Sequence as _Sequence,
    MutableSequence as _MutableSequence,
    Set as _Set,
    Sized as _Sized,
)
from enum import (
    Enum as _Enum,
    EnumMeta as _EnumMeta,
)
from io import IOBase as _IOBase
from typing import Any

# Note that:
#
# * "BuiltinMethodType" is intentionally *NOT* imported, as that type is
#   exactly synonymous with "BuiltinFunctionType", implying C-based methods are
#   indistinguishable from C-based functions. To prevent C-based functions from
#   being misidentified as C-based methods, all C-based functions and methods
#   are ambiguously identified as C-based callables.
# * "LambdaType" is intentionally *NOT* imported, as that type is exactly
#   synonymous with "FunctionType", implying lambdas are indistinguishable from
#   pure-Python functions. To prevent pure-Python functions from being
#   misidentified as lambdas, all lambdas are currently misidentified as
#   pure-Python functions.
#
# These are the lesser of multiple evils.
from types import (
    AsyncGeneratorType as _AsyncGeneratorType,
    BuiltinFunctionType as _BuiltinFunctionType,
    CellType as _CellType,
    CoroutineType as _CoroutineType,
    FrameType as _FrameType,
    FunctionType as _FunctionType,
    GeneratorType as _GeneratorType,
    GetSetDescriptorType as _GetSetDescriptorType,
    MemberDescriptorType as _MemberDescriptorType,
    MethodType as _MethodType,
    ModuleType as _ModuleType,
    TracebackType as _TracebackType,
)

# ....................{ IMPORTS ~ conditional              }....................
#FIXME: Preserve for when we inevitably require similar logic in the future.

# # Attempt to import types unavailable under Python 3.5, all of which should
# # be passed through the intermediary _get_type_or_unavailable() helper
# # function first before being assigned to module globals below. The
# # docstrings for such globals should contain a sentence resembling:
# #     **This type is unavailable under Python 3.5,** where it defaults to
# #     :class:`UnavailableType` for safety.
# try:
#     _Collection = type(list[str])
# # If this is Python 3.5, define placeholder globals of the same name.
# except ImportError:
#     _Collection = None

# ....................{ CLASSES                            }....................
class UnavailableType(object):
    '''
    **Unavailable type** (i.e., type *not* available under the active Python
    interpreter, typically due to insufficient Python version or non-installed
    third-party dependencies).
    '''

    def __instancecheck__(self, obj) -> None:
        raise BeartypeCallUnavailableTypeException(
            f'{self} not passable as the second parameter to isinstance().')

    def __subclasscheck__(self, cls) -> None:
        raise BeartypeCallUnavailableTypeException(
            f'{self} not passable as the second parameter to issubclass().')


# This is private, as it's unclear whether anyone requires access to this yet.
class _UnavailableTypesTuple(tuple):
    '''
    Type of any **tuple of unavailable types** (i.e., types *not* available
    under the active Python interpreter, typically due to insufficient Python
    version or non-installed third-party dependencies).
    '''

    pass

# ....................{ TYPES ~ core                       }....................
AnyType = object
'''
Type of all objects regardless of type.
'''


ClassType = type
'''
Type of all types.
'''


FileType = _IOBase
'''
Abstract base class of all **file-like objects** (i.e., objects implementing
the standard ``read()``, ``write()``, and ``close()`` methods).
'''


ModuleType = _ModuleType
'''
Type of all **C- and Python-based modules** (i.e., importable files implemented
either as C extensions or in pure Python).
'''

# ....................{ TYPES ~ core : singleton           }....................
EllipsisType: type = type(Ellipsis)
'''
Type of the :data:`Ellipsis` singleton.
'''


NoneType: type = type(None)
'''
Type of the :data:`None` singleton.

Curiously, although the type of the :data:`None` object is a class object whose
``__name__`` attribute is ``NoneType``, there exists no globally accessible
class by that name. To circumvents this obvious oversight, this global globally
exposes this class.

This class is principally useful for annotating both:

* Callable parameters accepting :data:`None` as a valid value.
* Callables returning :data:`None` as a valid value.

Note that, for obscure and uninteresting reasons, the standard :mod:`types`
module defined the same type with the same name under Python 2.x but *not* 3.x.
Depressingly, this type must now be manually redefined everywhere.
'''


NotImplementedType: type = type(NotImplemented)  # type: ignore[misc]
'''
Type of the :data:`NotImplemented` singleton.
'''

# ....................{ TYPES ~ call                       }....................
CallablePartialType = _functools.partial
'''
Type of all **pure-Python partial callables** (i.e., callables dynamically
wrapped by the function-like :class:`functools.partial` class, implemented in
pure Python).

Caveats
----------
This type does *not* distinguish between whether the original callable wrapped
by :class:`functools.partial` is C-based or pure Python -- only that some
callable of indeterminate origin is in fact wrapped.
'''


CallableCodeObjectType: Any = type((lambda: None).__code__)
'''
Type of all **code objects** (i.e., C-based objects underlying all pure-Python
callables to which those callables are compiled for efficiency).
'''


# Alias this type to this standard type.
#
# Note that this is explicitly required for "nuitka" support, which supports
# this standard type but *NOT* the non-standard approach used to deduce this
# type under Python 3.7 leveraged below.
ClosureVarCellType = _CellType
'''
Type of all **pure-Python closure cell variables.**
'''

# ....................{ TYPES ~ call : exception           }....................
ExceptionTracebackType = _TracebackType
'''
Type of all **traceback objects** (i.e., C-based objects comprising the full
stack traces associated with raised exceptions).
'''


CallableFrameType = _FrameType
'''
Type of all **call stack frame objects** (i.e., C-based objects
encapsulating each call to each callable on the current call stack).
'''

# ....................{ TYPES ~ call : function            }....................
FunctionType = _FunctionType
'''
Type of all **pure-Python functions** (i.e., functions implemented in Python
*not* associated with an owning class or instance of a class).

Caveats
----------
**This type ambiguously matches many callables not commonly associated with
standard functions,** including:

* **Lambda functions.** Of course, distinguishing between conventional named
  functions and unnamed lambda functions would usually be seen as overly
  specific. So, this ambiguity is *not* necessarily a bad thing.
* **Unbound instance methods** (i.e., instance methods accessed on their
  declaring classes rather than bound instances).
* **Static methods** (i.e., methods decorated with the builtin
  :func:`staticmethod` decorator, regardless of whether those methods are
  accessed on their declaring classes or associated instances).

**This type matches no callables whatsoever under some non-CPython
interpreters,** including:

* PyPy, which unconditionally compiles *all* pure-Python functions into C-based
  functions. Ergo, under PyPy, *all* functions are guaranteed to be of the type
  :class:`FunctionOrMethodCType` regardless of whether those functions were
  initially defined in Python or C.

See Also
----------
:class:`MethodBoundInstanceOrClassType`
    Type of all pure-Python bound instance and class methods.
'''


FunctionOrMethodCType = _BuiltinFunctionType
'''
Type of all **C-based callables** (i.e., functions and methods implemented with
low-level C rather than high-level Python, typically either in third-party C
extensions, official stdlib C extensions, or the active Python interpreter
itself).
'''

# ....................{ TYPES ~ call : method : bound      }....................
MethodBoundInstanceOrClassType = _MethodType
'''
Type of all **pure-Python bound instance and class methods** (i.e., methods
implemented in pure Python, bound to either instances of classes or classes
*and* implicitly passed those instances or classes as their first parameters).

Caveats
----------
There exists *no* corresponding :class:`MethodUnboundInstanceType` type, as
unbound pure-Python instance methods are ambiguously implemented as functions of
type :class:`FunctionType` indistinguishable from conventional functions.
Indeed, `official documentation <PyInstanceMethod_Type documentation_>`__ for
the ``PyInstanceMethod_Type`` C type explicitly admits that:

    This instance of PyTypeObject represents the Python instance method type.
    It is not exposed to Python programs.

.. _PyInstanceMethod_Type documentation:
   https://docs.python.org/3/c-api/method.html#c.PyInstanceMethod_Type
'''


# Although Python >= 3.7 now exposes an explicit method wrapper type via the
# standard "types.MethodWrapperType" object, this is of no benefit to older
# versions of Python. Ergo, the type of an arbitrary method wrapper guaranteed
# to *ALWAYS* exist is obtained instead.
MethodBoundInstanceDunderCType: Any = type(''.__add__)
'''
Type of all **C-based bound method wrappers** (i.e., callable objects
implemented in low-level C, associated with special methods of builtin types
when accessed as instance rather than class attributes).

See Also
----------
:class:`MethodUnboundInstanceDunderCType`
    Type of all C-based unbound dunder method wrapper descriptors.
'''

# ....................{ TYPES ~ call : method : unbound    }....................
# Although Python >= 3.7 now exposes an explicit method wrapper type via the
# standard "types.ClassMethodDescriptorType" object, this is of no benefit to
# older versions of Python. Ergo, the type of an arbitrary method descriptor
# guaranteed to *ALWAYS* exist is obtained instead.
MethodUnboundClassCType: Any = type(dict.__dict__['fromkeys'])
'''
Type of all **C-based unbound class method descriptors** (i.e., callable objects
implemented in low-level C, associated with class methods of builtin types when
accessed with the low-level :attr:`object.__dict__` dictionary rather than as
class or instance attributes).

Despite being unbound, class method descriptors remain callable (e.g., by
explicitly passing the intended ``cls`` objects as their first parameters).
'''


# Although Python >= 3.7 now exposes an explicit method wrapper type via the
# standard "types.WrapperDescriptorType" object, this is of no benefit to older
# versions of Python. Ergo, the type of an arbitrary method descriptor
# guaranteed to *ALWAYS* exist is obtained instead.
MethodUnboundInstanceDunderCType: Any = type(str.__add__)
'''
Type of all **C-based unbound dunder method wrapper descriptors** (i.e.,
callable objects implemented in low-level C, associated with dunder methods of
builtin types when accessed as class rather than instance attributes).

Despite being unbound, method descriptor wrappers remain callable (e.g., by
explicitly passing the intended ``self`` objects as their first parameters).

See Also
----------
:class:`MethodBoundInstanceDunderCType`
    Type of all C-based unbound dunder method wrappers.
:class:`MethodUnboundInstanceNondunderCType`
    Type of all C-based unbound non-dunder method descriptors.
'''


# Although Python >= 3.7 now exposes an explicit method wrapper type via the
# standard "types.MethodDescriptorType" object, this is of no benefit to older
# versions of Python. Ergo, the type of an arbitrary method descriptor
# guaranteed to *ALWAYS* exist is obtained instead.
MethodUnboundInstanceNondunderCType: Any = type(str.upper)
'''
Type of all **C-based unbound non-dunder method descriptors** (i.e., callable
objects implemented in low-level C, associated with non-dunder methods of
builtin types when accessed as class rather than instance attributes).

Despite being unbound, method descriptors remain callable (e.g., by explicitly
passing the intended ``self`` objects as their first parameters).

See Also
----------
:class:`MethodUnboundInstanceDunderCType`
    Type of all C-based unbound dunder method wrapper descriptors.
'''


MethodUnboundPropertyNontrivialCExtensionType = _GetSetDescriptorType
'''
Type of all **C extension-specific unbound non-trivial property method
descriptors** (i.e., uncallable objects implemented in low-level C extensions,
associated with **non-trivial property methods** (i.e., wrapping underlying
attributes that are *not* trivially convertible to C types) of C extensions when
accessed with the low-level :attr:`object.__dict__` dictionary rather than as
class or instance attributes).
'''


MethodUnboundPropertyTrivialCExtensionType = _MemberDescriptorType
'''
Type of all **C extension-specific unbound trivial property method descriptors**
(i.e., uncallable objects implemented in low-level C extensions, associated with
**trivial property methods** (i.e., wrapping underlying attributes that are
trivially convertible to C types) of C extensions when accessed with the
low-level :attr:`object.__dict__` dictionary rather than as class or instance
attributes).
'''

# ....................{ TYPES ~ call : method : decorator  }....................
MethodDecoratorClassType = classmethod
'''
Type of all **C-based unbound class method descriptors** (i.e., non-callable
instances of the builtin :class:`classmethod` decorator class implemented in
low-level C, associated with class methods implemented in pure Python, and
accessed with the low-level :attr:`object.__dict__` dictionary rather than as
class or instance attributes).

Caveats
----------
Class method objects are *only* directly accessible via the low-level
:attr:`object.__dict__` dictionary. When accessed as class or instance
attributes, class methods reduce to instances of the standard
:class:`MethodBoundInstanceOrClassType` type.

Class method objects are *not* callable, as their implementations fail to
define the ``__call__`` dunder method.
'''


MethodDecoratorPropertyType = property
'''
Type of all **C-based unbound property method descriptors** (i.e., non-callable
instances of the builtin :class:`property` decorator class implemented in
low-level C, associated with property getter and setter methods implemented in
pure Python, and accessed as class rather than instance attributes).

Caveats
----------
Property objects are directly accessible both as class attributes *and* via the
low-level :attr:`object.__dict__` dictionary. Property objects are *not*
accessible as instance attributes, for hopefully obvious reasons.

Property objects are *not* callable, as their implementations fail to define
the ``__call__`` dunder method.
'''


MethodDecoratorStaticType = staticmethod
'''
Type of all **C-based unbound static method descriptors** (i.e., non-callable
instances of the builtin :class:`classmethod` decorator class implemented in
low-level C, associated with static methods implemented in pure Python, and
accessed with the low-level :attr:`object.__dict__` dictionary rather than as
class or instance attributes).

Caveats
----------
Static method objects are *only* directly accessible via the low-level
:attr:`object.__dict__` dictionary. When accessed as class or instance
attributes, static methods reduce to instances of the standard
:class:`FunctionType` type.

Static method objects are *not* callable, as their implementations fail to
define the ``__call__`` dunder method.
'''

# ....................{ TYPES ~ call : return : async      }....................
AsyncGeneratorCType = _AsyncGeneratorType
'''
C-based type returned by all **asynchronous pure-Python generators** (i.e.,
callables implemented in pure Python containing one or more ``yield``
statements whose declaration is preceded by the ``async`` keyword).

Caveats
----------
**This is not the type of asynchronous generator callables** but rather the
type implicitly created and *returned* by these callables. Since these
callables are simply callables subject to syntactic sugar, the type of these
callables is simply :data:`CallableTypes`.
'''


AsyncCoroutineCType = _CoroutineType
'''
C-based type returned by all **asynchronous coroutines** (i.e., callables
implemented in pure Python *not* containing one or more ``yield`` statements
whose declaration is preceded by the ``async`` keyword).

Caveats
----------
**This is not the type of asynchronous coroutine callables** but rather the
type implicitly created and *returned* by these callables. Since these
callables are simply callables subject to syntactic sugar, the type of these
callables is simply :data:`CallableTypes`.
'''

# ....................{ TYPES ~ call : return : generator  }....................
GeneratorType = _Generator
'''
Type of all **C- and Python-based generator objects** (i.e., iterators
implementing the :class:`collections.abc.Generator` protocol), including:

* Pure-Python subclasses of the :class:`collections.abc.Generator` superclass.
* C-based generators returned by pure-Python callables containing one or more
  ``yield`` statements.
* C-based generator comprehensions created by pure-Python syntax delimited by
  ``(`` and ``)``.

Caveats
----------
**This is not the type of generator callables** but rather the type implicitly
created and *returned* by these callables. Since these callables are simply
callables subject to syntactic sugar, the type of these callables is simply
:data:`CallableTypes`.

See Also
----------
:class:`GeneratorCType`
    Subtype of all C-based generators.
'''


GeneratorCType = _GeneratorType
'''
C-based type returned by all **pure-Python generators** (i.e., callables
implemented in pure Python containing one or more ``yield`` statements,
implicitly converted at runtime to return a C-based iterator of this type) as
well as the C-based type of all **pure-Python generator comprehensions** (i.e.,
``(``- and ``)``-delimited syntactic sugar implemented in pure Python, also
implicitly converted at runtime to return a C-based iterator of this type).

Caveats
----------
**This is not the type of generator callables** but rather the type implicitly
created and *returned* by these callables. Since these callables are simply
callables subject to syntactic sugar, the type of these callables is simply
:data:`CallableTypes`.

This special-purpose type is a subtype of the more general-purpose
:class:`GeneratorType`. Whereas the latter applies to *all* generators
implementing the :class:`collections.abc.Iterator` protocol, the former only
applies to generators implicitly created by Python itself.
'''

# ....................{ TYPES ~ class                      }....................
ClassDictType = type(type.__dict__)
'''
Type of all **pure-Python class dictionaries** (i.e., immutable mappings
officially referred to as "mapping proxies," whose keys are strictly constrained
for both efficiency and correctness to be Python identifier strings).
'''

# ....................{ TYPES ~ data                       }....................
ContainerType = _Container
'''
Type of all **containers** (i.e., concrete instances of the abstract
:class:`collections.abc.Container` base class as well as arbitrary objects
whose classes implement all abstract methods declared by that base class
regardless of whether those classes actually subclass that base class).

Caveats
----------
This type ambiguously matches both:

* **Explicit container subtypes** (i.e., concrete subclasses of the
  :class:`collections.abc.Container` abstract base class (ABC)).
* **Structural container subtypes** (i.e., arbitrary classes implementing the
  abstract ``__contains__`` method declared by that ABC *without* subclassing
  that ABC), as formalized by :pep:`544`. Notably, since the **NumPy array
  type** (i.e., :class:`numpy.ndarray`) defines that method, this type magically
  matches the NumPy array type as well.

Of course, distinguishing between explicit and structural subtypes would
usually be seen as overly specific. So, this ambiguity is *not* necessarily a
BadThing™.

What is a BadThing™ is that container ABCs violate the "explicit is better than
implicit" maxim of `PEP 20 -- The Zen of Python <PEP 20_>`__ by intentionally
deceiving you for your own benefit, which you of course appreciate. Thanks to
arcane dunder magics buried in the :class:`abc.ABCMeta` metaclass, the
:func:`isinstance` and :func:`issubclass` builtin functions (which the
:func:`beartype.beartype` decorator internally defers to) ambiguously mistype
structural container subtypes as explicit container subtypes:

.. code-block:: python

   >>> from collections.abc import Container
   >>> class FakeContainer(object):
   ...     def __contains__(self, obj): return True
   >>> FakeContainer.__mro__
   ... (FakeContainer, object)
   >>> issubclass(FakeContainer, Container)
   True
   >>> isinstance(FakeContainer(), Container)
   True

.. _PEP 20:
   https://www.python.org/dev/peps/pep-0020
'''


IterableType = _Iterable
'''
Type of all **iterables** (i.e., both concrete and structural instances of the
abstract :class:`collections.abc.Iterable` base class).

Iterables are containers that may be indirectly iterated over by calling the
:func:`iter` builtin, which internally calls the ``__iter__()`` dunder methods
implemented by these containers, which return **iterators** (i.e., instances of
the :class:`IteratorType` type), which directly support iteration.

This type also matches **NumPy arrays** (i.e., instances of the concrete
:class:`numpy.ndarray` class) via structural subtyping.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
:class:`IteratorType`
    Further details on iteration.
'''


IteratorType = _Iterator
'''
Type of all **iterators** (i.e., both concrete and structural instances of
the abstract :class:`collections.abc.Iterator` base class; objects iterating
over associated data streams, which are typically containers).

Iterators implement at least two dunder methods:

* ``__next__()``, iteratively returning successive items from associated data
  streams (e.g., container objects) until throwing standard
  :data:`StopIteration` exceptions on reaching the ends of those streams.
* ``__iter__()``, returning themselves. Since iterables (i.e., instances of the
  :class:`IterableType` type) are *only* required to implement the
  ``__iter__()`` dunder method, all iterators are by definition iterables as
  well.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
:class:`IterableType`
    Further details on iteration.
'''


SizedType = _Sized
'''
Type of all **sized containers** (i.e., both concrete and structural instances
of the abstract :class:`collections.abc.Sized` base class; containers defining
the ``__len__()`` dunder method internally called by the :func:`len` builtin).

This type also matches **NumPy arrays** (i.e., instances of the concrete
:class:`numpy.ndarray` class) via structural subtyping.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''


CollectionType = _Collection
'''
Type of all **collections** (i.e., both concrete and structural instances of
the abstract :class:`collections.abc.Collection` base class; sized iterable
containers defining the ``__contains__()``, ``__iter__()``, and ``__len__()``
dunder methods).

This type also matches **NumPy arrays** (i.e., instances of the concrete
:class:`numpy.ndarray` class) via structural subtyping.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''


QueueType = _deque
'''
Type of all **double-ended queues** (i.e., instances of the concrete
:class:`collections.deque` class, the only queue type defined by the Python
stdlib).

Caveats
----------
The :mod:`collections.abc` subpackage currently provides no corresponding
abstract interface to formalize queue types. Double-ended queues are it, sadly.
'''


SetType = _Set
'''
Type of all **set-like containers** (i.e., both concrete and structural
instances of the abstract :class:`collections.abc.Set` base class; containers
guaranteeing uniqueness across all contained items).

This type matches both the standard :class:`set` and :class:`frozenset` types
*and* the types of the :class:`dict`-specific views returned by the
:meth:`dict.items` and :meth:`dict.keys` (but *not* :meth:`dict.values`)
methods.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''

# ....................{ TYPES ~ data : mapping             }....................
HashableType = _Hashable
'''
Type of all **hashable objects** (i.e., both concrete and structural instances
of the abstract :class:`collections.abc.Hashable` base class; objects
implementing the ``__hash__()`` dunder method required for all dictionary keys
and set items).

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''


MappingType = _Mapping
'''
Type of all **mutable** and **immutable mappings** (i.e., both concrete and
structural instances of the abstract :class:`collections.abc.Mapping` base
class; dictionary-like containers containing key-value pairs mapping from
hashable keys to corresponding values).

Caveats
----------
**This type does not guarantee mutability** (i.e., the capacity to modify
instances of this type after instantiation). This type ambiguously matches both
mutable mapping types (e.g., :class:`dict`) and immutable mapping types (e.g.,
:class:`ClassDictType`). Where mutability is required, prefer the non-ambiguous
:class:`MappingMutableType` type instead.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''


MappingMutableType = _MutableMapping
'''
Type of all **mutable mappings** (i.e., both concrete and structural instances
of the abstract :class:`collections.abc.MutableMapping` base class;
dictionary-like containers permitting modification of contained key-value
pairs).

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
:class:`MappingType`
    Type of all mutable and immutable mappings.
'''

# ....................{ TYPES ~ data : sequence            }....................
SequenceType = _Sequence
'''
Type of all **mutable** and **immutable sequences** (i.e., both concrete and
structural instances of the abstract :class:`collections.abc.Sequence` base
class; reversible collections whose items are efficiently accessible but *not*
necessarily modifiable with 0-based integer-indexed lookup).

Caveats
----------
**This type does not guarantee mutability** (i.e., the capacity to modify
instances of this type after instantiation). This type ambiguously matches both
mutable sequence types (e.g., :class:`list`) and immutable sequence types
(e.g., :class:`tuple`). Where mutability is required, prefer the non-ambiguous
:class:`SequenceMutableType` type instead.

**This type matches the string type (i.e., :class:`str`),** which satisfies the
:class:`collections.abc.Sequence` API but *not* the
:class:`collections.abc.MutableSequence` API. Where **non-string sequences**
(i.e., sequences that are anything but strings) are required, prefer the
non-ambiguous :class:`SequenceMutableType` type instead.

**This type does not match NumPy arrays (i.e., instances of the concrete
:class:`numpy.ndarray` class),** which satisfy most but *not* all of the
:class:`collections.abc.Sequence` API. Specifically, NumPy arrays fail to
define:

* The ``__reversible__`` dunder method.
* The ``count`` public method.
* The ``index`` public method.

Most callables accepting sequences *never* invoke these edge-case methods and
should thus be typed to accept NumPy arrays as well. To do so, prefer either:

* The :class:`beartype.cave.SequenceOrNumpyArrayTypes` tuple of types matching
  both sequences and NumPy arrays.
* The :class:`beartype.cave.SequenceMutableOrNumpyArrayTypes` tuple of types
  matching both mutable sequences and NumPy arrays.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
'''


SequenceMutableType = _MutableSequence
'''
Type of all **mutable sequences** (i.e., both concrete and structural instances
of the abstract :class:`collections.abc.Sequence` base class; reversible
collections whose items are both efficiently accessible *and* modifiable with
0-based integer-indexed lookup).

Caveats
----------
**This type does not match NumPy arrays (i.e., instances of the concrete
:class:`numpy.ndarray` class),** which satisfy most but *not* all of the
:class:`collections.abc.MutableSequence` API. Specifically, NumPy arrays fail
to define:

* The ``__reversible__`` dunder method.
* The ``append`` public method.
* The ``count`` public method.
* The ``extend`` public method.
* The ``index`` public method.
* The ``insert`` public method.
* The ``pop`` public method.
* The ``remove`` public method.
* The ``reverse`` public method.

Most callables accepting mutable sequences *never* invoke these edge-case
methods and should thus be typed to accept NumPy arrays as well. To do so,
prefer the :class:`beartype.cave.SequenceMutableOrNumpyArrayTypes` tuple of
types matching both mutable sequences and NumPy arrays.

See Also
----------
:class:`ContainerType`
    Further details on structural subtyping.
:class:`SequenceType`
    Further details on sequences.
'''

# ....................{ TYPES ~ enum                       }....................
# Enumeration types are sufficiently obscure to warrant formalization here.

EnumType = _EnumMeta
'''
Type of all **enumeration types** (i.e., metaclass of all classes containing
all enumeration members comprising those enumerations).

Motivation
----------
This type is commonly used to validate callable parameters as enumerations. In
recognition of its popularity, this type is intentionally named ``EnumType``
rather than ``EnumMetaType``. While the latter *would* technically be less
ambiguous, the former has the advantage of inviting correctness throughout
downstream codebases -- a less abundant resource.

Why? Because *all* enumeration types are instances of this type rather than the
:class:`Enum` class despite being superficially defined as instances of the
:class:`Enum` class. Thanks to metaclass abuse, enumeration types do *not*
adhere to standard Pythonic semantics. Notably, the following non-standard
invariants hold across *all* enumerations:

.. code-block:: python

   >>> from enum import Enum
   >>> GyreType = Enum(
   ...     'GyreType', ('THE', 'FALCON', 'CANNOT', 'HEAR', 'THE', 'FALCONER'))
   >>> from beartype import cave
   >>> isinstance(GyreType, Enum)
   False
   >>> isinstance(GyreType, cave.EnumType)
   True
   >>> isinstance(GyreType, cave.ClassType)
   True
   >>> isinstance(GyreType.FALCON, cave.EnumType)
   False
   >>> isinstance(GyreType.FALCON, cave.EnumMemberType)
   True
   >>> isinstance(GyreType.FALCON, cave.ClassType)
   False

Yes, this is insane. Yes, this is Python.
'''


EnumMemberType = _Enum
'''
Type of all **enumeration members** (i.e., abstract base class of all
alternative choices defined as enumeration fields).

Caveats
----------
When type checking callable parameters, this class should *only* be referenced
where the callable permissively accepts any enumeration member type rather than
a specific enumeration member type. In the latter case, that type is simply
that enumeration's type and should be directly referenced as such: e.g.,

    >>> from enum import Enum
    >>> from beartype import beartype
    >>> EndymionType = Enum('EndymionType', ('BEAUTY', 'JOY',))
    >>> @beartype
    ... def our_feet_were_soft_in_flowers(superlative: EndymionType) -> str:
    ...     return str(superlative).lower()
'''

# ....................{ TYPES ~ hint                       }....................
# Define this type as either...
HintGenericSubscriptedType: Any = (
    # If the active Python interpreter targets at least Python >= 3.9 and thus
    # supports PEP 585, this type;
    type(list[str])  # type: ignore[misc]
    if IS_PYTHON_AT_LEAST_3_9 else
    # Else, a placeholder type.
    UnavailableType
)
'''
C-based type of all subscripted generics if the active Python interpreter
targets Python >= 3.9 *or* :class:`UnavailableType` otherwise.

Subscripted generics include:

* :pep:`585`-compliant **builtin type hints** (i.e., C-based type hints
  instantiated by subscripting either a concrete builtin container class like
  :class:`list` or :class:`tuple` *or* an abstract base class (ABC) declared by
  the :mod:`collections.abc` submodule like :class:`collections.abc.Iterable`
  or :class:`collections.abc.Sequence`). Since *all* :pep:`585`-compliant
  builtin type hints are classes, this C-based type is the class of those
  classes and thus effectively itself a metaclass. It's probably best not to
  think about that.
* :pep:`484`-compliant **subscripted generics** (i.e., user-defined classes
  subclassing one or more :pep:`484`-compliant type hints subsequently
  subscripted by one or more PEP-compliant type hints).
* :pep:`585`-compliant **subscripted generics** (i.e., user-defined classes
  subclassing one or more :pep:`585`-compliant type hints subsequently
  subscripted by one or more PEP-compliant type hints).

Caveats
----------
**This low-level type ambiguously matches semantically unrelated PEP-compliant
type hints,** rendering this type all but useless for most practical purposes.
To distinguish between the various semantic types of hints ambiguously matched
by this type, higher-level PEP-specific functions *must* be called instead.
These include:

* :func:`beartype._util.hint.pep.proposal.pep484.utilpep484.is_hint_pep484_generic`,
  detecting :pep:`484`-compliant generic type hints.
* :func:`beartype._util.hint.pep.proposal.utilpep585.is_hint_pep585_builtin`,
  detecting :pep:`585`-compliant builtin type hints.
* :func:`beartype._util.hint.pep.proposal.utilpep585.is_hint_pep585_generic`,
  detecting :pep:`585`-compliant generic type hints.
'''

# ....................{ TYPES ~ scalar                     }....................
StrType = str    # Well, isn't that special.
'''
Type of all **unencoded Unicode strings** (i.e., instances of the builtin
:class:`str` class; sequences of abstract Unicode codepoints that have yet to
be encoded into physical encoded bytes in encoded byte strings).

This type matches:

* **Builtin Unicode strings** (i.e., :class:`str` instances).
* **NumPy Unicode strings** (i.e., :class:`numpy.str_` instances) if
  :mod:`numpy` is importable. Whereas most NumPy scalar types do *not* subclass
  builtin scalar types, the :class:`numpy.str_` class *does* subclass the
  builtin :class:`str` type. NumPy Unicode strings are thus usable wherever
  builtin Unicode strings are usable.

Caveats
----------
This type does *not* match **encoded byte strings** (i.e., sequences of
physical encoded bytes, including the builtin :class:`bytestring` type), which
require foreknowledge of the encoding previously used to encode those bytes.
Unencoded Unicode strings require no such foreknowledge and are thus
incompatible with encoded byte strings at the API level.

This type only matches **builtin Unicode strings** (i.e., :class:`str`
instances) and instances of subtypes of that type (e.g., :class:`numpy.str_`,
the NumPy Unicode string type). Whereas the comparable :class:`BoolType`
matches arbitrary objects satisfying the boolean protocol (i.e., ``__bool__()``
dunder method) via structural subtyping, this type does *not* match arbitrary
objects satisfying the string protocol via structural subtyping -- because
there is no string protocol. While Python's data model does define a
``__str__()`` dunder method called to implicitly convert arbitrary objects into
strings, that method is called infrequently. As exhibited by the infamously
rejected :pep:`3140` proposal, the :meth:`list.__str__` implementation
stringifies list items by erroneously calling the unrelated ``__repr__()``
method rather than the expected ``__str__()`` method on those items. Moreover,
``__str__()`` fails to cover common string operations such as string
concatenation and repetition. Covering those operations would require a new
abstract base class (ABC) matching arbitrary objects satisfying the
:class:`Sequence` protocol as well as ``__str__()`` via structural subtyping;
while trivial, that ABC would then ambiguously match all builtin sequence types
(e.g., :class:`list`, :class:`tuple`) as string types, which they clearly are
not. In short, matching only :class:`str` is the *only* unambiguous means of
matching Unicode string types.
'''

# ....................{ TYPES ~ scalar : number            }....................
NumberType = _numbers.Number
'''
Type of all **numbers** (i.e., concrete instances of the abstract
:class:`numbers.Number` base class).

This type effectively matches *all* numbers regardless of implementation,
including:

* **Integers** (i.e., real numbers expressible without fractional components),
  including:
  * **Builtin integers** (i.e., :class:`int` instances).
  * **NumPy integers** (e.g., :class:`numpy.int_` instances), whose types are
    all implicitly registered at :mod:`numpy` importation time as satisfying
    the :class:`numbers.Integral` protocol.
  * **SymPy integers** (e.g., :class:`sympy.core.numbers.Integer` instances),
    whose type is implicitly registered at :mod:`sympy` importation time as
    satisfying the class:`numbers.Integral` protocol.
* **Rational numbers** (i.e., real numbers expressible as the ratio of two
  integers), including:
  * **Builtin floating-point numbers** (i.e., :class:`float` instances).
  * **NumPy floating-point numbers** (e.g., :class:`numpy.single` instances),
    all of which are implicitly registered at :mod:`numpy` importation time as
    :class:`numbers.Rational` subclasses.
  * **Stdlib fractions** (i.e., :class:`fractions.Fraction` instances).
  * **SymPy floating-point numbers** (e.g., :class:`sympy.core.numbers.Float`
    instances), whose type implicitly registered at :mod:`sympy` importation
    time as satisfying the class:`numbers.Real` protocol.
  * **SymPy rational numbers** (e.g., :class:`sympy.core.numbers.Rational`
    instances), whose type implicitly registered at :mod:`sympy` importation
    time as satisfying the class:`numbers.Rational` protocol.
* **Irrational numbers** (i.e., real numbers *not* expressible as the ratio of
  two integers), including:
  * **SymPy irrational numbers** (i.e., SymPy-specific symbolic objects whose
    ``is_irrational`` assumption evaluates to ``True``).

Caveats
----------
This type does *not* match:

* **Stdlib decimals** (i.e., :class:`decimal.Decimal` instances), which support
  both unrounded decimal (i.e., fixed-point arithmetic) and rounded
  floating-point arithmetic. Despite being strictly rational, the
  :class:`decimal.Decimal` class only subclasses the coarse-grained abstract
  :class:`numbers.Number` base superclass rather than the fine-grained abstract
  :class:`numbers.Rational` base subclass. So it goes.
* **SymPy complex numbers,** which are "non-atomic" (i.e., defined as the
  combination of two separate real and imaginary components rather than as one
  unified complex number containing these components) and thus incommensurable
  with all of the above "atomic" types.
'''


NumberRealType = IntOrFloatType = _numbers.Real
'''
Type of all **real numbers** (i.e., concrete instances of the abstract
:class:`numbers.Real` base class; numbers expressible as linear values on the
real number line).

This type matches all numbers matched by :class:`NumberType` *except* complex
numbers with non-zero imaginary components, which (as the name implies) are
non-real.

Equivalently, this type matches all integers (e.g., :class:`int`,
:class:`numpy.int_`), floating-point numbers (e.g., :class:`float`,
:class:`numpy.single`), rational numbers (e.g., :class:`fractions.Fraction`,
:class:`sympy.core.numbers.Rational`), and irrational numbers. However,
rational and irrational numbers are rarely used in comparison to integers and
floating-point numbers. This type thus reduces to matching all integer and
floating-point types in practice and is thus also accessible under the alias
:class:`IntOrFloatType` -- a less accurate but more readable name than
:class:`NumberRealType`.

See Also
----------
:class:`NumberType`
    Further details.
'''


IntType = _numbers.Integral
'''
Type of all **integers** (i.e., concrete instances of the abstract
:class:`numbers.Integral` base class; real numbers expressible without
fractional components).

This type matches all numbers matched by the :class:`NumberType` *except*
complex numbers with non-zero imaginary components, rational numbers with
denominators not equal to one, and irrational numbers.

Equivalently, this type matches all integers (e.g., :class:`int`,
:class:`numpy.int_`).

See Also
----------
:class:`NumberType`
    Further details.
'''

# ....................{ TYPES ~ stdlib : re                }....................
# Regular expression types are also sufficiently obscure to warrant
# formalization here.

# Yes, this is the only reliable means of obtaining the type of compiled
# regular expressions. For unknown reasons presumably concerning the archaic
# nature of Python's regular expression support, this type is *NOT* publicly
# exposed. While the private "re._pattern_type" attribute does technically
# provide this type, it does so in a private and hence non-portable manner.
RegexCompiledType: type = _re.Pattern
'''
Type of all **compiled regular expressions** (i.e., objects created and
returned by the stdlib :func:`re.compile` function).
'''


# Yes, this type is required for type validation at module scope elsewhere.
# Yes, this is the most time-efficient means of obtaining this type. No, this
# type is *NOT* directly importable. Although this type's classname is
# published to be "_sre.SRE_Match", the "_sre" C extension provides no such
# type for pure-Python importation. So it goes.
RegexMatchType: type = _re.Match
'''
Type of all **regular expression match objects** (i.e., objects returned by the
:func:`re.match` function).
'''

# ....................{ TUPLES ~ unavailable               }....................
# Unavailable types are defined *BEFORE* any subsequent types, as the latter
# commonly leverage the former.

UnavailableTypes = _UnavailableTypesTuple()
'''
**Tuple of unavailable types** (i.e., types *not* available under the active
Python interpreter, typically due to insufficient Python version or
non-installed third-party dependencies).

Caveats
----------
**This tuple should always be used in lieu of the empty tuple.** Although
technically equivalent to the empty tuple, the :func:`beartype.beartype`
decorator explicitly distinguishes between this tuple and the empty tuple.
Specifically, for any callable parameter or return type annotated with:

* This tuple, :func:`beartype.beartype` emits a non-fatal warning ignorable
  with a simple :mod:`warnings` filter.
* The empty tuple, :func:`beartype.beartype` raises a fatal exception.
'''

# ....................{ TUPLES ~ py                        }....................
ModuleOrStrTypes = (ModuleType, StrType)
'''
Tuple of both the module *and* string type.
'''


#FIXME: This is probably incorrect under Python >= 3.9, where isinstance() also
#accepts "|"-delimited unions of types (e.g., float | int | str). What are
#those types, exactly?
TestableTypes = (ClassType, tuple)
'''
Tuple of all **testable types** (i.e., types suitable for use as the second
parameter passed to the :func:`isinstance` and :func:`issubclass` builtins).
'''

# ....................{ TUPLES ~ call                      }....................
FunctionTypes = (FunctionType, FunctionOrMethodCType,)
'''
Tuple of all **function types** (i.e., types whose instances are either
built-in or user-defined functions).

Caveats
----------
**This tuple may yield false positives when used to validate types.** Since
Python fails to distinguish between C-based functions and methods, this tuple
is the set of all function types as well as the ambiguous type of all C-based
functions and methods.
'''

# ....................{ TUPLES ~ call : method             }....................
MethodBoundTypes = (
    MethodBoundInstanceOrClassType, MethodBoundInstanceDunderCType)
'''
Tuple of all **bound method types** (i.e., types whose instances are callable
objects bound to either instances or classes).
'''


MethodUnboundTypes = (
    MethodUnboundClassCType,
    MethodUnboundInstanceDunderCType,
    MethodUnboundInstanceNondunderCType,
)
'''
Tuple of all **unbound method types** (i.e., types whose instances are callable
objects bound to neither instances nor classes).

Unbound decorator objects (e.g., non-callable instances of the builtin
:class:`classmethod`, :class:`property`, or :class:`staticmethod` decorator
classes) are *not* callable and thus intentionally excluded.
'''


MethodDecoratorBuiltinTypes = (
    MethodDecoratorClassType,
    MethodDecoratorPropertyType,
    MethodDecoratorStaticType,
)
'''
Tuple of all **C-based unbound method decorator types** (i.e., builtin decorator
types implemented in low-level C whose instances are typically uncallable,
associated with callable methods implemented in pure Python).
'''


MethodDescriptorTypes = (
    # @classmethod, @staticmethod, and @property descriptor types.
    MethodDecoratorBuiltinTypes + (
        # Method descriptor type.
        MethodBoundInstanceOrClassType,
    )
)
'''
Tuple of all **C-based unbound method descriptor types** (i.e., builtin types
implemented in low-level C whose instances are typically uncallable, associated
with callable methods implemented in pure Python).

This tuple matches the types of all:

* **Class method descriptors** (i.e., methods decorated by the builtin
  :class:`classmethod` decorator).
* Instance method descriptors (i.e., methods *not* decorated by a builtin method
  decorator).
* **Property method descriptors** (i.e., methods decorated by the builtin
  :class:`property` decorator).
* **Static method descriptors** (i.e., methods decorated by the builtin
  :class:`staticmethod` decorator).
'''


MethodTypes = (FunctionOrMethodCType,) + MethodBoundTypes + MethodUnboundTypes
'''
Tuple of all **method types** (i.e., types whose instances are callable objects
associated with methods implemented in either low-level C or pure Python).

Unbound decorator objects (e.g., non-callable instances of the builtin
:class:`classmethod`, :class:`property`, or :class:`staticmethod` decorator
classes) are *not* callable and thus intentionally excluded.

Caveats
----------
**This tuple may yield false positives when used to validate types.** Since
Python fails to distinguish between C-based functions and methods, this tuple
is the set of all pure-Python bound and unbound method types as well as the
ambiguous type of all C-based bound methods and non-method functions.
'''

# ....................{ TUPLES ~ call : callable           }....................
# For DRY, this tuple is defined as the set union of all function and method
# types defined above converted back to a tuple.
#
# While this tuple could also be defined as the simple concatenation of the
# "FunctionTypes" and "MethodTypes" tuples, doing so would duplicate all types
# ambiguously residing in both tuples (i.e., "FunctionOrMethodCType"). Doing so
# would induce inefficiencies during type checking. That would be bad.
CallableTypes = tuple(set(FunctionTypes) | set(MethodTypes))
'''
Tuple of all **callable types** (i.e., types whose instances are callable
objects implemented in either low-level C or high-level Python, including both
built-in and user-defined functions, lambdas, methods, and method descriptors).
'''


CallableCTypes = (
    FunctionOrMethodCType,
    MethodBoundInstanceDunderCType,
    MethodUnboundInstanceDunderCType,
    MethodUnboundInstanceNondunderCType,
    MethodUnboundClassCType,
)
'''
Tuple of all **C-based callable types** (i.e., types whose instances are
callable objects implemented in low-level C rather than high-level Python).
'''


CallablePyTypes = (
    FunctionType,
    MethodBoundInstanceOrClassType,
)
'''
Tuple of all **pure-Python callable types** (i.e., types whose instances are
callable objects implemented in high-level Python rather than low-level C).

**This tuple is empty under PyPy,** which unconditionally compiles *all*
pure-Python callables into C-based callables.
'''


CallableOrClassTypes = CallableTypes + (ClassType,)
'''
Tuple of all callable types as well as the type of all types.
'''


CallableOrStrTypes = CallableTypes + (StrType,)
'''
Tuple of all callable types as well as the string type.
'''


#FIXME: Define a new "CallableClassType" by copying the "BoolType" approach
#except for the __call__() dunder method instead.
#FIXME: Replace "ClassType" below by "CallableClassType".
#FIXME: Add the "CallableClassType" type to the "CallableTypes" tuple as well.
DecoratorTypes = CallableTypes + (ClassType,)
'''
Tuple of all **decorator types** (i.e., both callable classes *and* the type of
those classes).

Caveats
----------
**This tuple may yield false positives when used to validate types.** Since
classes themselves may be callable (i.e., by defining the special ``__call__``
method), this tuple is the set of all standard callable types as well as that
of classes. In particular, this tuple describes all types permissible for use
as decorators. Since most classes are *not* callable, however, this tuple may
yield false positives when passed classes.
'''

# ....................{ TUPLES ~ call : return             }....................
AsyncCTypes = (AsyncGeneratorCType, AsyncCoroutineCType)
'''
Tuple of all C-based types returned by all **asynchronous callables** (i.e.,
callables implemented in pure Python whose declaration is preceded by the
``async`` keyword).
'''

# ....................{ TUPLES ~ scalar                    }....................
BoolOrNumberTypes = (BoolType, NumberType,)
'''
Tuple of all **boolean** and **number types** (i.e., classes whose instances
are either numbers or types trivially convertible into numbers).

This tuple matches booleans, integers, rational numbers, irrational numbers,
real numbers, and complex numbers.

Booleans are trivially convertible into integers. While details differ by
implementation, common implementations in lower-level languages (e.g., C, C++,
Perl) typically implicitly convert:

* ``False`` to ``0`` and vice versa.
* ``True`` to ``1`` and vice versa.
'''

# ....................{ TUPLES ~ post-init : container     }....................
# Tuples of types assuming the above initialization to have been performed.

MappingOrSequenceTypes = (MappingType, SequenceType)
'''
Tuple of all container base classes conforming to (but *not* necessarily
subclassing) the canonical :class:`collections.abc.Mapping` *or*
:class:`collections.abc.Sequence` APIs.
'''


ModuleOrSequenceTypes = (ModuleType, SequenceType)
'''
Tuple of the module type *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`collections.abc.Sequence`
API.
'''


NumberOrIterableTypes = (NumberType, IterableType,)
'''
Tuple of all numeric types *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`collections.abc.Iterable`
API.
'''


NumberOrSequenceTypes = (NumberType, SequenceType,)
'''
Tuple of all numeric types *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`collections.abc.Sequence`
API.
'''

# ....................{ TUPLES ~ post-init : scalar        }....................
ScalarTypes = BoolOrNumberTypes + (StrType,)
'''
Tuple of all **scalar types** (i.e., classes whose instances are atomic scalar
primitives).

This tuple matches all:

* **Boolean types** (i.e., types satisfying the :class:`BoolType` protocol).
* **Numeric types** (i.e., types satisfying the :class:`NumberType` protocol).
* **Textual types** (i.e., types contained in the :class:`StrTypes` tuple).
'''

# ....................{ TUPLES ~ stdlib                    }....................
RegexTypes = (RegexCompiledType, StrType)
'''
Tuple of all **regular expression-like types** (i.e., types either defining
regular expressions or losslessly convertible to such types).

This tuple matches:

* The **compiled regular expression type** (i.e., type of all objects created
  and returned by the stdlib :func:`re.compile` function).
* All **textual types** (i.e., types contained in the :class:`StrTypes`
  tuple).
'''
