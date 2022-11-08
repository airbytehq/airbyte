#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


class UndefinedReferenceException(Exception):
    """
    Raised when refering to an undefined reference.
    """

    def __init__(self, path, reference):
        super().__init__(f"Undefined reference {reference} from {path}")
