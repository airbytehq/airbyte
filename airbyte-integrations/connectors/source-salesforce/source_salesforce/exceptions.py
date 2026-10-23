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

# Strings come from Salesforce's documented responses and still need confirming against a live org.
CLIENT_CREDENTIALS_ERROR_MESSAGE_MAPPING = {
    "request not supported on this domain": "Salesforce accepts client credentials only at your org's My Domain URL. Enter the URL shown in Salesforce Setup under My Domain.",
    "client identifier invalid": "Salesforce doesn't recognize the Client ID. Enter the consumer key of your External Client App.",
    "invalid client credentials": "Salesforce rejected the Client Secret. Enter the consumer secret of your External Client App.",
    "no client credentials user enabled": "The External Client App has no Run As user for the client credentials flow. Set Run As to your integration user in the app's policies.",
}
CLIENT_CREDENTIALS_REJECTED_MESSAGE = (
    "Salesforce rejected the client credentials. Check Client ID, Client Secret and My Domain URL against your External Client App."
)
MISSING_DOMAIN_URL_MESSAGE = (
    "My Domain URL is required for the ClientCredentials method. Enter the URL shown in Salesforce Setup under My Domain."
)
MISSING_CLIENT_CREDENTIALS_MESSAGE = "Client ID and Client Secret are not set for the ClientCredentials method. Enter the consumer key and consumer secret of your External Client App."
MISSING_REFRESH_TOKEN_MESSAGE = (
    "Refresh Token is missing for the Client method. Authenticate your Salesforce account, or select ClientCredentials."
)


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
