
import requests
from airbyte_cdk import AirbyteLogger


class Error(Exception):
    """ Base Error class for other exceptions """
    logger = AirbyteLogger()

class ZOQLQueryError(Error):
    """ Base class for  ZOQL EXPORT query errors """

    def __init__(self, response: requests.Response):
        self.response = response.json()
        self.error_msg = self.response["data"]["errorMessage"]
        self.query = self.response["data"]["query"]
        super().__init__(self.logger.warn(f'{self.error_msg}, QUERY: {self.query}'))

class ZOQLQueryFailed(ZOQLQueryError):
    """ Failed to execute query on the server side """

class ZOQLQueryCanceledOrAborted(ZOQLQueryError):
    """ The query is canceled and not going to execute on the server side"""

class EndDateError(Error):
    """ The error occures when the START DATE is bigger than END DATE """

    def __init__(self, message = "'End Date' should be bigger than 'Start Date'!"):
        self.message = message
        super().__init__(self.logger.error(self.message))