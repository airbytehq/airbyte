#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Mapping


@dataclass
class TypeTransformer(ABC):
    """
    Abstract base class for implementing type transformation logic.

    This class provides a blueprint for defining custom transformations
    on data records based on a provided schema. Implementing classes
    must override the `transform` method to specify the transformation
    logic.

    Attributes:
        None explicitly defined, as this is a dataclass intended to be
        subclassed.

    Methods:
        transform(record: Dict[str, Any], schema: Mapping[str, Any]) -> None:
            Abstract method that must be implemented by subclasses.
            It performs a transformation on a given data record based
            on the provided schema.

    Usage:
        To use this class, create a subclass that implements the
        `transform` method with the desired transformation logic.
    """

    @abstractmethod
    def transform(
        self,
        record: Dict[str, Any],
        schema: Mapping[str, Any],
    ) -> None:
        """
        Perform a transformation on a data record based on a given schema.

        Args:
            record (Dict[str, Any]): The data record to be transformed.
            schema (Mapping[str, Any]): The schema that dictates how
                the record should be transformed.

        Returns:
            None

        Raises:
            NotImplementedError: If the method is not implemented
                by a subclass.
        """
