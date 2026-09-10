#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging


# Maps the lower-cased error_description returned by the Salesforce token endpoint to a user-actionable
# message. Lives here (not in rate_limiting) so both api.py and rate_limiting.py can use it without a
# module-level import cycle. Keys must be lower case: Salesforce is not consistent about capitalizing
# these descriptions, so the lookup normalizes the incoming value.
AUTHENTICATION_ERROR_MESSAGE_MAPPING = {
    "expired access/refresh token": "The authentication to SalesForce has expired. Re-authenticate to restore access to SalesForce.",
    # OAuth 2.0 JWT Bearer flow rejections. Salesforce answers HTTP 400 invalid_grant with one of these
    # terse descriptions, none of which say what to change.
    # https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_flow_errors.htm
    "invalid assertion": (
        "Salesforce rejected the JWT assertion. Check that the Private Key matches the certificate uploaded to the "
        "connected app's \"Use digital signatures\" setting, and that the Client ID is that app's Consumer Key."
    ),
    "invalid audience": (
        "Salesforce rejected the JWT assertion audience. Set the Sandbox option to match the org you are connecting to: "
        "sandboxes authenticate against test.salesforce.com, production orgs against login.salesforce.com."
    ),
    "invalid user": (
        "Salesforce does not recognize the configured Username. Enter the exact Salesforce username the connector should "
        "authenticate as. Sandbox usernames carry the sandbox name as a suffix, for example user@example.com.sandboxname."
    ),
    "user hasn't approved this consumer": (
        "The configured Username is not authorized for the connected app. Set the app's OAuth policy to "
        '"Admin approved users are pre-authorized" and assign the user through a permission set or profile.'
    ),
}

# Raised once a login has been rejected for good. The refresh-token wording above does not apply to the
# JWT Bearer flow: it issues no refresh token, so there is nothing to re-authenticate and the connected
# app or the JWT inputs are what has to change.
JWT_AUTHENTICATION_FAILED_MESSAGE = (
    "Salesforce rejected the JWT Bearer authentication. Verify the connected app's digital-signature certificate, its "
    "OAuth scopes (refresh_token plus at least one standard scope such as api), and that the configured Username is "
    "pre-authorized for the app."
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
