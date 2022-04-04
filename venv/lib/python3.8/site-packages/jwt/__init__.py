from .api_jwk import PyJWK, PyJWKSet
from .api_jws import (
    PyJWS,
    get_unverified_header,
    register_algorithm,
    unregister_algorithm,
)
from .api_jwt import PyJWT, decode, encode
from .exceptions import (
    DecodeError,
    ExpiredSignatureError,
    ImmatureSignatureError,
    InvalidAlgorithmError,
    InvalidAudienceError,
    InvalidIssuedAtError,
    InvalidIssuerError,
    InvalidKeyError,
    InvalidSignatureError,
    InvalidTokenError,
    MissingRequiredClaimError,
    PyJWKClientError,
    PyJWKError,
    PyJWKSetError,
    PyJWTError,
)
from .jwks_client import PyJWKClient

__version__ = "2.3.0"

__title__ = "PyJWT"
__description__ = "JSON Web Token implementation in Python"
__url__ = "https://pyjwt.readthedocs.io"
__uri__ = __url__
__doc__ = __description__ + " <" + __uri__ + ">"

__author__ = "José Padilla"
__email__ = "hello@jpadilla.com"

__license__ = "MIT"
__copyright__ = "Copyright 2015-2020 José Padilla"


__all__ = [
    "PyJWS",
    "PyJWT",
    "PyJWKClient",
    "PyJWK",
    "PyJWKSet",
    "decode",
    "encode",
    "get_unverified_header",
    "register_algorithm",
    "unregister_algorithm",
    # Exceptions
    "DecodeError",
    "ExpiredSignatureError",
    "ImmatureSignatureError",
    "InvalidAlgorithmError",
    "InvalidAudienceError",
    "InvalidIssuedAtError",
    "InvalidIssuerError",
    "InvalidKeyError",
    "InvalidSignatureError",
    "InvalidTokenError",
    "MissingRequiredClaimError",
    "PyJWKClientError",
    "PyJWKError",
    "PyJWKSetError",
    "PyJWTError",
]
