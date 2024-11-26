#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **caching metaclasses** (i.e., classes performing general-purpose
memoization of classes that declare the former to be their metaclasses).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Dict,
    Optional,
    Tuple,
    Type,
    TypeVar,
)
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ PRIVATE ~ hints                    }....................
_T = TypeVar('_T')
'''
PEP-compliant type variable matching any arbitrary object.
'''

# ....................{ METACLASSES                        }....................
class BeartypeCachingMeta(type):
    '''
    **Caching metaclass** (i.e., metaclass caching immutable instances of
    classes whose metaclasses are this metaclass, cached via the positional
    arguments instantiating those classes).

    This metaclass is superior to the usual approach of caching immutable
    objects: overriding the ``__new__`` method to conditionally create a new
    instance of that class only if an instance has *not* already been created
    with the passed positional arguments. Why? Because that approach unavoidably
    re-calls the ``__init__`` method of a previously initialized instance on
    each instantiation of that class -- which is clearly harmful, especially
    where immutability is concerned.

    This metaclass instead guarantees that the ``__init__`` method of an
    instance is only called once on the first instantiation of that instance.

    Caveats
    ----------
    **This metaclass assumes immutability.** Ideally, instances of classes whose
    metaclasses are this metaclass should be **immutable** (i.e., frozen). Where
    this is *not* the case, the behaviour of this metaclass is undefined.

    **This metaclass prohibits keyword arguments.** ``__init__`` methods of
    classes whose metaclass is this metaclass must accept *only* positional
    arguments. Why? Efficiency, the entire point of caching. While feasible,
    permitting ``__init__`` methods to also accept keyword arguments would be
    sufficiently slow as to entirely defeat the point of caching. That's bad.

    See Also
    ----------
    https://stackoverflow.com/a/8665179/2809027
        StackOverflow answers strongly inspiring this implementation.
    '''

    # ..................{ INITIALIZERS                       }..................
    @callable_cached
    def __call__(cls: Type[_T], *args) -> _T:
        '''
        Instantiate the passed class with the passed positional arguments if
        this is the first instantiation of this class passed these arguments
        *or* simply return the previously instantiated instance of this class
        otherwise (i.e., if this is a subsequent instantiation of this class
        re-passed these same arguments).

        Caveats
        ----------
        This method intentionally accepts *only* positional arguments. See the
        metaclass docstring for further details.

        Parameters
        ----------
        cls : type
            Class whose class is this metaclass.

        All remaining parameters are passed as is to the superclass
        :meth:`type.__call__` method.
        '''

        # Bear witness to the terrifying power of @callable_cached.
        return super().__call__(*args)  # type: ignore[misc]
