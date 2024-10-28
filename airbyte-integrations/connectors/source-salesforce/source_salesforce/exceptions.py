#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging


class Error(Exception):
    """Base Error class for other exceptions"""

    # Define the instance of the Native Airbyte Logger
    logger = logging.getLogger("airbyte")


class SalesforceException(Exception):
    """
    Default Salesforce exception.
    """


class TypeSalesforceException(SalesforceException):
    """
    We use this exception for unknown input data types for Salesforce.
    """


class TmpFileIOError(Error):
    def __init__(self, msg: str, err: str = None):
        self.logger.fatal(f"{msg}. Error: {err}")
