#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping


@dataclass
class DataclassOptionsMixin:
    """
    Mixin class used to extend the functionality of declarative components to allow for dynamic runtime options to be stored
    on instances without being part of the schema.

    Because dataclasses don't support dynamic fields, this class is used to take in an arbitrary set of parameters and assigns
    them to the _options field.

    Attributes:
        options (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
    """

    options: InitVar[Mapping[str, Any]]  # This field cannot have a default value since it comes before required child fields

    InitVar.__call__ = lambda *args: None
