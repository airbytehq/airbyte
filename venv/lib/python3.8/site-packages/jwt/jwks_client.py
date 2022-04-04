import json
import urllib.request
from functools import lru_cache
from typing import Any, List

from .api_jwk import PyJWK, PyJWKSet
from .api_jwt import decode_complete as decode_token
from .exceptions import PyJWKClientError


class PyJWKClient:
    def __init__(self, uri: str, cache_keys: bool = True, max_cached_keys: int = 16):
        self.uri = uri
        if cache_keys:
            # Cache signing keys
            # Ignore mypy (https://github.com/python/mypy/issues/2427)
            self.get_signing_key = lru_cache(maxsize=max_cached_keys)(self.get_signing_key)  # type: ignore

    def fetch_data(self) -> Any:
        with urllib.request.urlopen(self.uri) as response:
            return json.load(response)

    def get_jwk_set(self) -> PyJWKSet:
        data = self.fetch_data()
        return PyJWKSet.from_dict(data)

    def get_signing_keys(self) -> List[PyJWK]:
        jwk_set = self.get_jwk_set()
        signing_keys = [
            jwk_set_key
            for jwk_set_key in jwk_set.keys
            if jwk_set_key.public_key_use in ["sig", None] and jwk_set_key.key_id
        ]

        if not signing_keys:
            raise PyJWKClientError("The JWKS endpoint did not contain any signing keys")

        return signing_keys

    def get_signing_key(self, kid: str) -> PyJWK:
        signing_keys = self.get_signing_keys()
        signing_key = None

        for key in signing_keys:
            if key.key_id == kid:
                signing_key = key
                break

        if not signing_key:
            raise PyJWKClientError(
                f'Unable to find a signing key that matches: "{kid}"'
            )

        return signing_key

    def get_signing_key_from_jwt(self, token: str) -> PyJWK:
        unverified = decode_token(token, options={"verify_signature": False})
        header = unverified["header"]
        return self.get_signing_key(header.get("kid"))
