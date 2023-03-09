#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


class CircularReferenceException(Exception):
    """
    Raised when a circular reference is detected in a manifest.
    """

    def __init__(self, reference):
        super().__init__(f"Circular reference found: {reference}")


class UndefinedReferenceException(Exception):
    """
    Raised when refering to an undefined reference.
    """

    def __init__(self, path, reference):
        super().__init__(f"Undefined reference {reference} from {path}")
