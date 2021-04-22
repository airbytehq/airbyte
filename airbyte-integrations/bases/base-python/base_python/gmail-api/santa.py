from typing import Mapping, Any, Iterable, Optional, List, Tuple

import sys
import requests

from base_python import Stream, AirbyteLogger
from base_python.entrypoint import launch
from sdk.streams.auth.oauth import Oauth2Authenticator
from sdk.abstract_source import AbstractSource
from sdk.streams.http import HttpStream

# Fill in from Lastpass Airbyte Gmail API Token shared note.
google_authenticator = Oauth2Authenticator(
    client_id='',
    client_secret='',
    refresh_token='',
    token_refresh_endpoint=''
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
