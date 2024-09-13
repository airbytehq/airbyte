#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import base64
import logging
from datetime import datetime

import freezegun
import jwt
import pytest
from airbyte_cdk.sources.declarative.auth.jwt import JwtAuthenticator

LOGGER = logging.getLogger(__name__)


class TestJwtAuthenticator:
    """
    Test class for JWT Authenticator.
    """

    @pytest.mark.parametrize(
        "algorithm, kid, typ, cty, additional_jwt_headers, expected",
        [
            (
                "ALGORITHM",
                "test_kid",
                "test_typ",
                "test_cty",
                {"test": "test"},
                {"kid": "test_kid", "typ": "test_typ", "cty": "test_cty", "test": "test", "alg": "ALGORITHM"},
            ),
            ("ALGORITHM", None, None, None, None, {"alg": "ALGORITHM"}),
        ],
    )
    def test_get_jwt_headers(self, algorithm, kid, typ, cty, additional_jwt_headers, expected):
        authenticator = JwtAuthenticator(
            config={},
            parameters={},
            algorithm=algorithm,
            secret_key="test_key",
            token_duration=1200,
            kid=kid,
            typ=typ,
            cty=cty,
            additional_jwt_headers=additional_jwt_headers,
        )
        assert authenticator._get_jwt_headers() == expected

    def test_given_overriden_reserverd_properties_get_jwt_headers_throws_error(self):
        authenticator = JwtAuthenticator(
            config={},
            parameters={},
            algorithm="ALGORITHM",
            secret_key="test_key",
            token_duration=1200,
            additional_jwt_headers={"kid": "test_kid"},
        )
        with pytest.raises(ValueError):
            authenticator._get_jwt_headers()

    @pytest.mark.parametrize(
        "iss, sub, aud, additional_jwt_payload, expected",
        [
            (
                "test_iss",
                "test_sub",
                "test_aud",
                {"test": "test"},
                {"iss": "test_iss", "sub": "test_sub", "aud": "test_aud", "test": "test"},
            ),
            (None, None, None, None, {}),
        ],
    )
    def test_get_jwt_payload(self, iss, sub, aud, additional_jwt_payload, expected):
        authenticator = JwtAuthenticator(
            config={},
            parameters={},
            algorithm="ALGORITHM",
            secret_key="test_key",
            token_duration=1000,
            iss=iss,
            sub=sub,
            aud=aud,
            additional_jwt_payload=additional_jwt_payload,
        )
        with freezegun.freeze_time("2022-01-01 00:00:00"):
            expected["iat"] = int(datetime.now().timestamp())
            expected["exp"] = expected["iat"] + 1000
            expected["nbf"] = expected["iat"]
            assert authenticator._get_jwt_payload() == expected

    def test_given_overriden_reserverd_properties_get_jwt_payload_throws_error(self):
        authenticator = JwtAuthenticator(
            config={},
            parameters={},
            algorithm="ALGORITHM",
            secret_key="test_key",
            token_duration=0,
            additional_jwt_payload={"exp": 1234},
        )
        with pytest.raises(ValueError):
            authenticator._get_jwt_payload()

    @pytest.mark.parametrize(
        "base64_encode_secret_key, secret_key, expected",
        [
            (True, "test", base64.b64encode("test".encode()).decode()),
            (False, "test", "test"),
        ],
    )
    def test_get_secret_key(self, base64_encode_secret_key, secret_key, expected):
        authenticator = JwtAuthenticator(
            config={},
            parameters={},
            secret_key=secret_key,
            algorithm="test_algo",
            token_duration=1200,
            base64_encode_secret_key=base64_encode_secret_key,
        )
        assert authenticator._get_secret_key() == expected

    def test_get_signed_token(self):
        authenticator = JwtAuthenticator(
            config={},
            parameters={},
            secret_key="test",
            algorithm="HS256",
            token_duration=1000,
            typ="JWT",
            iss="iss",
        )
        assert authenticator._get_signed_token() == jwt.encode(
            payload=authenticator._get_jwt_payload(),
            key=authenticator._get_secret_key(),
            algorithm=authenticator._algorithm,
            headers=authenticator._get_jwt_headers(),
        )

    def test_given_invalid_algorithm_get_signed_token_throws_error(self):
        authenticator = JwtAuthenticator(
            config={},
            parameters={},
            secret_key="test",
            algorithm="invalid algorithm type",
            token_duration=1000,
            base64_encode_secret_key=False,
            header_prefix="Bearer",
            typ="JWT",
            iss="iss",
            additional_jwt_headers={},
            additional_jwt_payload={},
        )
        with pytest.raises(ValueError):
            authenticator._get_signed_token()

    @pytest.mark.parametrize("header_prefix, expected", [("test", "test"), (None, None)])
    def test_get_header_prefix(self, header_prefix, expected):
        authenticator = JwtAuthenticator(
            config={},
            parameters={},
            secret_key="key",
            algorithm="test_algo",
            token_duration=1200,
            header_prefix=header_prefix,
        )
        assert authenticator._get_header_prefix() == expected
