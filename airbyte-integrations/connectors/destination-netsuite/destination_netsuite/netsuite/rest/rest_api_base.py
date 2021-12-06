import asyncio
import logging

import httpx
from authlib.integrations.httpx_client import OAuth1Auth
from authlib.oauth1.rfc5849.client_auth import ClientAuth
from authlib.oauth1.rfc5849.signature import generate_signature_base_string
from oauthlib.oauth1.rfc5849.signature import sign_hmac_sha256_with_client

from . import json
from destination_netsuite.netsuite.error import NetsuiteAPIRequestError, NetsuiteAPIResponseParsingError
from destination_netsuite.netsuite.configuration import cached_property

__all__ = ("RestApiBase",)

DEFAULT_SIGNATURE_METHOD = "HMAC-SHA256"

logger = logging.getLogger(__name__)


def authlib_hmac_sha256_sign_method(client, request):
    """Sign a HMAC-SHA256 signature."""
    base_string = generate_signature_base_string(request)
    # return sign_hmac_sha256(base_string, client.client_secret, client.token_secret)
    return sign_hmac_sha256_with_client(base_string, client)


ClientAuth.register_signature_method(
    "HMAC-SHA256", authlib_hmac_sha256_sign_method)

class OAuth1(OAuth1Auth):
    def __init__(self, 
                client_id, 
                client_secret,
                token, 
                token_secret,
                signature_method,
                realm,
                force_include_body):
        super().__init__(
                client_id=client_id, 
                client_secret=client_secret,
                token=token,
                token_secret=token_secret,
                signature_method=signature_method,
                realm=realm,
                force_include_body=force_include_body)
        self.resource_owner_secret=token_secret        

class RestApiBase:
    _concurrent_requests: int = 10
    _default_timeout: int = 10
    _signature_method: str = DEFAULT_SIGNATURE_METHOD

    @cached_property
    def _request_semaphore(self) -> asyncio.Semaphore:
        # NOTE: Shouldn't be put in __init__ as we might not have a running
        #       event loop at that time.
        return asyncio.Semaphore(self._concurrent_requests)

    async def _request(self, method: str, subpath: str, **request_kw):
        resp = await self._request_impl(method, subpath, **request_kw)

        if resp.status_code < 200 or resp.status_code > 299:
            raise NetsuiteAPIRequestError(resp.status_code, resp.text)

        if resp.status_code == 204:
            return None
        else:
            try:
                return json.loads(resp.text)
            except Exception:
                raise NetsuiteAPIResponseParsingError(
                    resp.status_code, resp.text)

    async def _request_impl(
        self, method: str, subpath: str, **request_kw
    ) -> httpx.Response:
        method = method.upper()
        url = self._make_url(subpath)

        headers = {**self._make_default_headers(), **
                   request_kw.pop("headers", {})}

        timeout = request_kw.pop("timeout", self._default_timeout)

        if "json" in request_kw:
            request_kw["data"] = json.dumps(request_kw.pop("json"))

        kw = {**request_kw}
        logger.debug(
            f"Making {method.upper()} request to {url}. Keyword arguments: {kw}"
        )

        async with self._request_semaphore:
            async with httpx.AsyncClient() as c:
                resp = await c.request(
                    method=method,
                    url=url,
                    headers=headers,
                    auth=self._make_auth(),
                    timeout=timeout,
                    **kw,
                )

        resp_headers_json = json.dumps(dict(resp.headers))
        logger.debug(
            f"Got response headers from NetSuite: {resp_headers_json}")

        return resp

    def _make_url(self, subpath: str):
        raise NotImplementedError

    def _make_auth(self):
        auth = self._config.token_auth
        return OAuth1(
            client_id=auth.consumer_key,
            client_secret=auth.consumer_secret,
            token=auth.token_id,
            token_secret=auth.token_secret,
            realm=self._config.get_account_id(),
            force_include_body=True,
            signature_method=self._signature_method,
        )

    def _make_default_headers(self):
        return {"Content-Type": "application/json"}
