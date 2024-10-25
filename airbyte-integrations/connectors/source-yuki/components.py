import re
from dataclasses import dataclass
from http import HTTPStatus
from typing import Union, Mapping, Any

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config
import requests
from requests import HTTPError


# See Yuki docs: https://documenter.getpostman.com/view/12207912/UVCBB51L#1b9c831e-0fad-41ef-b098-c2fee51ffeed
# SessionID is a session token with a lifetime of 24h

@dataclass
class CustomAuthenticator(NoAuth):
    config: Config
    api_key: Union[InterpolatedString, str]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.api_key = InterpolatedString(self.api_key, parameters=parameters).eval(self.config)

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Inject the session token into the request body"""
        # As there is no refresh endpoint provided by Yuki API, we need to generate a new token for each request
        session_id = self.generate_access_token()
        request.body = re.sub(r"<they:sessionID>.*?</they:sessionID>", f"<they:sessionID>{session_id}</they:sessionID>", request.body)
        return request

    def generate_access_token(self) -> tuple[str, str]:
        try:
            headers = {"Content-Type": "application/xml"}
            data = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:they="http://www.theyukicompany.com/">
               <soapenv:Header/>
               <soapenv:Body>
                  <they:Authenticate>
                     <they:accessKey>{self.api_key}</they:accessKey>
                  </they:Authenticate>
               </soapenv:Body>
            </soapenv:Envelope>
            """
            url = "https://api.yukiworks.be/ws/Sales.asmx?WSDL"
            res = requests.post(url, headers=headers, data=data)
            if res.status_code != HTTPStatus.OK:
                raise HTTPError(res.text)
            session_id = re.search(r"<AuthenticateResult>(.*)</AuthenticateResult>", res.text).group(1)
            return session_id
        except Exception as e:
            raise Exception(f"Error while generating session token: {e}") from e
