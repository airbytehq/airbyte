#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Set, Union


class InvalidSiteURLValidationError(Exception):
    def __init__(self, invalid_site_url: Union[Set, List]) -> None:
        message = f'The following URLs are not permitted: {", ".join(invalid_site_url)}'
        super().__init__(message)


class UnauthorizedOauthError(Exception):
    def __init__(self):
        message = "Unable to connect with provided OAuth credentials. The `access token` or `refresh token` is expired. Please re-authrenticate using valid account credenials."
        super().__init__(message)


class UnauthorizedServiceAccountError(Exception):
    def __init__(self):
        message = (
            "Unable to connect with provided Service Account credentials. Make sure the `sevice account credentials` provided are valid."
        )
        super().__init__(message)


class UnidentifiedError(Exception):
    def __init__(self, error_body: Any):
        message = f"Unable to connect to Google Search Console API - {error_body}"
        super().__init__(message)
