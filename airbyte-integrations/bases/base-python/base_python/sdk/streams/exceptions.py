import requests


class BaseBackoffException(requests.exceptions.HTTPError):
    pass


class UserDefinedBackoffException(BaseBackoffException):
    """
    An exception that exposes how long it attempted to backoff
    """

    def __init__(self, backoff: int, request: requests.PreparedRequest, response: requests.Response):
        """
        :param backoff: how long to backoff in seconds
        :param request: the request that triggered this backoff exception
        :param response: the response that triggered the backoff exception
        """
        self.backoff = backoff
        super().__init__(request=request, response=response)


class DefaultBackoffException(BaseBackoffException):
    pass
