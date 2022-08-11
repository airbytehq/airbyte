#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


class ReadException(Exception):
    """
    Raise when there is an error reading data from an API Source
    """


class InvalidConnectorDefinitionException(Exception):
    """
    Raise when the connector definition is invalid
    """
