#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from requests.auth import AuthBase


class QueryStringTokenAuthenticator(AuthBase):
    """
    Authenticator that attaches a set of query string parameters (e.g. an API key) to the request.
    """

    def __init__(self, **kwargs):
        self.params = kwargs

    def __call__(self, request):
        if self.params:
            request.prepare_url(request.url, self.params)
        return request
