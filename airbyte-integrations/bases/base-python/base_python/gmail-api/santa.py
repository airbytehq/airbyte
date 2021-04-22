from typing import Mapping, Any, Iterable, Optional, List, Tuple

import sys
import requests

from base_python import Stream, AirbyteLogger
from base_python.entrypoint import launch
from sdk.streams.auth.oauth import Oauth2Authenticator
from sdk.abstract_source import AbstractSource
from sdk.streams.http import HttpStream

google_authenticator = Oauth2Authenticator(
    client_id='708867486045-aab3e9rtms70jr8be4rg19ckoqjrvil0.apps.googleusercontent.com',
    client_secret='9T6EkdO5g0-19R0SgboeFH6i',
    refresh_token='1//0gJ7K-A4VJie5CgYIARAAGBASNwF-L9IroEo5hjabu_w69DLQpryPCd6-ROFQmvM5dSkq1lOrmfYFt6sNkX-IJktT3gHGpHo5oZ8',
    token_refresh_endpoint='https://oauth2.googleapis.com/token'
)

class GmailUser(HttpStream):

    url_base = 'https://gmail.googleapis.com/gmail/v1/users/me/profile'

    def __init__(self, authenticator: Oauth2Authenticator):
        super().__init__(authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(self, **kwargs) -> str:
        print("path!")
        return ''


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        print(f'{response.json()}')
        yield[]

class GmailSource(AbstractSource):

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [GmailUser(google_authenticator)]


if __name__ == '__main__':
    print(f"Running..")
    launch(GmailSource(), sys.argv[1:])
