#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) API.**

This subpackage provides an object-oriented type hint class hierarchy,
encapsulating the crude non-object-oriented type hint declarative API
standardized by the :mod:`typing` module.
'''

# ....................{ TODO                               }....................
#FIXME: Create one unique "TypeHint" subclass *FOR EACH UNIQUE KIND OF TYPE
#HINT.* We're currently simply reusing the same
#"_TypeHintOriginIsinstanceableArgs*" family of concrete subclasses to
#transparently handle these unique kinds of type hints. That's fine as an
#internal implementation convenience. Sadly, that's *NOT* fine for users
#actually trying to introspect types. That's the great disadvantage of standard
#"typing" types, after all; they're *NOT* introspectable by type. Ergo, we need
#to explicitly define subclasses like:
#* "beartype.door.ListTypeHint".
#* "beartype.door.MappingTypeHint".
#* "beartype.door.SequenceTypeHint".
#
#And so on. There are a plethora, but ultimately a finite plethora, which is all
#that matters. Do this for our wonderful userbase, please.

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.door._cls.doorsuper import (
    TypeHint as TypeHint)
from beartype.door._doorcheck import (
    die_if_unbearable as die_if_unbearable,
    is_bearable as is_bearable,
    is_subhint as is_subhint,
)
from beartype.door._cls.pep.doorpep484604 import (
    UnionTypeHint as UnionTypeHint)
from beartype.door._cls.pep.doorpep586 import (
    LiteralTypeHint as LiteralTypeHint)
from beartype.door._cls.pep.doorpep593 import (
    AnnotatedTypeHint as AnnotatedTypeHint)
from beartype.door._cls.pep.pep484.doorpep484class import (
    ClassTypeHint as ClassTypeHint)
from beartype.door._cls.pep.pep484.doorpep484newtype import (
    NewTypeTypeHint as NewTypeTypeHint)
from beartype.door._cls.pep.pep484.doorpep484typevar import (
    TypeVarTypeHint as TypeVarTypeHint)
from beartype.door._cls.pep.pep484585.doorpep484585callable import (
    CallableTypeHint as CallableTypeHint)

#FIXME: Actually, let's *NOT* publicly expose this for the moment. Why? Because
#we still need to split this into fixed and variadic tuple subclasses.
# from beartype.door._cls.pep.pep484585.doorpep484585tuple import (
#     _TupleTypeHint as _TupleTypeHint)
