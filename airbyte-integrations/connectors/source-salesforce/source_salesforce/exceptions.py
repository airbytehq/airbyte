#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging


# Maps the error_description returned by the Salesforce token endpoint to a user-actionable message.
# Lives here (not in rate_limiting) so both api.py and rate_limiting.py can use it without a
# module-level import cycle.
AUTHENTICATION_ERROR_MESSAGE_MAPPING = {
    "expired access/refresh token": "The authentication to SalesForce has expired. Re-authenticate to restore access to SalesForce."
}


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
