import json
import logging
import re
from abc import ABC, abstractmethod
from base64 import b64encode
from typing import Any, Callable, Dict, Optional

try:
    import botocore
except ImportError:  # pragma: no cover
    # botocore is only needed for the IAM AppSync authentication method
    pass

log = logging.getLogger("gql.transport.appsync")


class AppSyncAuthentication(ABC):
    """AWS authentication abstract base class

    All AWS authentication class should have a
    :meth:`get_headers <gql.transport.appsync.AppSyncAuthentication.get_headers>`
    method which defines the headers used in the authentication process."""

    def get_auth_url(self, url: str) -> str:
        """
        :return: a url with base64 encoded headers used to establish
                 a websocket connection to the appsync-realtime-api.
        """
        headers = self.get_headers()

        encoded_headers = b64encode(
            json.dumps(headers, separators=(",", ":")).encode()
        ).decode()

        url_base = url.replace("https://", "wss://").replace(
            "appsync-api", "appsync-realtime-api"
        )

        return f"{url_base}?header={encoded_headers}&payload=e30="

    @abstractmethod
    def get_headers(
        self, data: Optional[str] = None, headers: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        raise NotImplementedError()  # pragma: no cover


class AppSyncApiKeyAuthentication(AppSyncAuthentication):
    """AWS authentication class using an API key"""

    def __init__(self, host: str, api_key: str) -> None:
        """
        :param host: the host, something like:
                     XXXXXXXXXXXXXXXXXXXXXXXXXX.appsync-api.REGION.amazonaws.com
        :param api_key: the API key
        """
        self._host = host.replace("appsync-realtime-api", "appsync-api")
        self.api_key = api_key

    def get_headers(
        self, data: Optional[str] = None, headers: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return {"host": self._host, "x-api-key": self.api_key}


class AppSyncJWTAuthentication(AppSyncAuthentication):
    """AWS authentication class using a JWT access token.

    It can be used either for:
     - Amazon Cognito user pools
     - OpenID Connect (OIDC)
    """

    def __init__(self, host: str, jwt: str) -> None:
        """
        :param host: the host, something like:
                     XXXXXXXXXXXXXXXXXXXXXXXXXX.appsync-api.REGION.amazonaws.com
        :param jwt: the JWT Access Token
        """
        self._host = host.replace("appsync-realtime-api", "appsync-api")
        self.jwt = jwt

    def get_headers(
        self, data: Optional[str] = None, headers: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return {"host": self._host, "Authorization": self.jwt}


class AppSyncIAMAuthentication(AppSyncAuthentication):
    """AWS authentication class using IAM.

    .. note::
        There is no need for you to use this class directly, you could instead
        intantiate the :class:`gql.transport.appsync.AppSyncWebsocketsTransport`
        without an auth argument.

    During initialization, this class will use botocore to attempt to
    find your IAM credentials, either from environment variables or
    from your AWS credentials file.
    """

    def __init__(
        self,
        host: str,
        region_name: Optional[str] = None,
        signer: Optional["botocore.auth.BaseSigner"] = None,
        request_creator: Optional[
            Callable[[Dict[str, Any]], "botocore.awsrequest.AWSRequest"]
        ] = None,
        credentials: Optional["botocore.credentials.Credentials"] = None,
        session: Optional["botocore.session.Session"] = None,
    ) -> None:
        """Initialize itself, saving the found credentials used
        to sign the headers later.

        if no credentials are found, then a NoCredentialsError is raised.
        """

        from botocore.auth import SigV4Auth
        from botocore.awsrequest import create_request_object
        from botocore.session import get_session

        self._host = host.replace("appsync-realtime-api", "appsync-api")
        self._session = session if session else get_session()
        self._credentials = (
            credentials if credentials else self._session.get_credentials()
        )
        self._service_name = "appsync"
        self._region_name = region_name or self._detect_region_name()
        self._signer = (
            signer
            if signer
            else SigV4Auth(self._credentials, self._service_name, self._region_name)
        )
        self._request_creator = (
            request_creator if request_creator else create_request_object
        )

    def _detect_region_name(self):
        """Try to detect the correct region_name.

        First try to extract the region_name from the host.

        If that does not work, then try to get the region_name from
        the aws configuration (~/.aws/config file) or the AWS_DEFAULT_REGION
        environment variable.

        If no region_name was found, then raise a NoRegionError exception."""

        from botocore.exceptions import NoRegionError

        # Regular expression from botocore.utils.validate_region
        m = re.search(
            r"appsync-api\.((?![0-9]+$)(?!-)[a-zA-Z0-9-]{,63}(?<!-))\.", self._host
        )

        if m:
            region_name = m.groups()[0]
            log.debug(f"Region name extracted from host: {region_name}")

        else:
            log.debug("Region name not found in host, trying default region name")
            region_name = self._session._resolve_region_name(
                None, self._session.get_default_client_config()
            )

        if region_name is None:
            log.warning(
                "Region name not found. "
                "It was not possible to detect your region either from the host "
                "or from your default AWS configuration."
            )
            raise NoRegionError

        return region_name

    def get_headers(
        self, data: Optional[str] = None, headers: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        from botocore.exceptions import NoCredentialsError

        # Default headers for a websocket connection
        headers = headers or {
            "accept": "application/json, text/javascript",
            "content-encoding": "amz-1.0",
            "content-type": "application/json; charset=UTF-8",
        }

        request: "botocore.awsrequest.AWSRequest" = self._request_creator(
            {
                "method": "POST",
                "url": f"https://{self._host}/graphql{'' if data else '/connect'}",
                "headers": headers,
                "context": {},
                "body": data or "{}",
            }
        )

        try:
            self._signer.add_auth(request)
        except NoCredentialsError:
            log.warning(
                "Credentials not found for the IAM auth. "
                "Do you have default AWS credentials configured?",
            )
            raise

        headers = dict(request.headers)

        headers["host"] = self._host

        if log.isEnabledFor(logging.DEBUG):
            headers_log = []
            headers_log.append("\n\nSigned headers:")
            for key, value in headers.items():
                headers_log.append(f"    {key}: {value}")
            headers_log.append("\n")
            log.debug("\n".join(headers_log))

        return headers
