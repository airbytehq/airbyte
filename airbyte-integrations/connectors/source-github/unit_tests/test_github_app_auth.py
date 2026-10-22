#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import threading

import jwt
import pytest
from components import ConfigNormalization, GithubAppMultiPemAuthenticator, _InstallationTokenCache, _parse_entries
from freezegun import freeze_time

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.auth.rate_limited_multiple_token import (
    RateLimitedMultipleTokenAuthenticator,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    SelectiveAuthenticator as SelectiveAuthenticatorModel,
)
from airbyte_cdk.utils import AirbyteTracedException

from .utils import make_source


# Captured before the autouse `_mock_jwt` fixture below stubs out `jwt.encode` for every test in
# this module, so tests that need the *real* signing failure path can restore it.
_REAL_JWT_ENCODE = jwt.encode


FAKE_PEM = (
    "-----BEGIN RSA PRIVATE KEY-----\nMIIBOgIBAAJBAKj34GkxFhD90vcNLYLInFEX6Ppy1tPf9Cnzj4p4WGeKLs1Pt8Qu\n-----END RSA PRIVATE KEY-----"
)


def _github_apps_field(*entries):
    return "\n\n".join(f"{app_id}\n{installation_id}\n{pem}" for app_id, installation_id, pem in entries)


def _access_token_url(installation_id):
    return f"https://api.github.com/app/installations/{installation_id}/access_tokens"


@pytest.fixture(autouse=True)
def _mock_jwt(monkeypatch):
    # Signing a real JWT needs a real RSA key; we only test our own usage of PyJWT, not PyJWT
    # itself, so stub it out with a deterministic fake.
    monkeypatch.setattr("components.jwt.encode", lambda payload, key, algorithm: "fake-app-jwt")


class TestParseEntries:
    def test_single_entry(self):
        assert _parse_entries(_github_apps_field(("111", "222", FAKE_PEM))) == [("111", "222", FAKE_PEM)]

    def test_multiple_entries_with_blank_lines_between(self):
        field = _github_apps_field(("111", "222", FAKE_PEM), ("333", "444", FAKE_PEM))
        entries = _parse_entries(field)
        assert [(app_id, installation_id) for app_id, installation_id, _ in entries] == [("111", "222"), ("333", "444")]

    def test_empty_string_returns_no_entries(self):
        assert _parse_entries("") == []

    def test_missing_installation_id_raises(self):
        with pytest.raises(ValueError, match="missing installation_id"):
            _parse_entries("111")

    def test_missing_pem_raises(self):
        with pytest.raises(ValueError, match="expected a '-----BEGIN"):
            _parse_entries("111\n222\nnot a pem")

    def test_unterminated_pem_raises(self):
        with pytest.raises(ValueError, match="never reached a '-----END"):
            _parse_entries("111\n222\n-----BEGIN RSA PRIVATE KEY-----\nAAAA")


class TestInstallationTokenMintingAndCaching:
    def test_mints_once_and_caches(self, requests_mock):
        mint_mock = requests_mock.post(_access_token_url("222"), json={"token": "ghs_abc"})
        requests_mock.get("https://api.github.com/rate_limit", json={"resources": {"core": {"remaining": 5000, "reset": 4070908800}}})
        authenticator = GithubAppMultiPemAuthenticator(config={}, parameters={}, github_apps=_github_apps_field(("111", "222", FAKE_PEM)))
        authenticator._ensure_ready()  # lazy: entries are only parsed/seeded on first actual use
        cache = authenticator._caches[0]
        assert cache.get_token() == "ghs_abc"
        assert cache.get_token() == "ghs_abc"
        assert mint_mock.call_count == 1  # _ensure_ready()'s refresh_quota() already minted once; both get_token() calls hit the cache

    def test_refreshes_after_expiry(self, requests_mock):
        requests_mock.post(_access_token_url("222"), [{"json": {"token": "ghs_first"}}, {"json": {"token": "ghs_second"}}])
        requests_mock.get("https://api.github.com/rate_limit", json={"resources": {"core": {"remaining": 5000, "reset": 4070908800}}})
        with freeze_time("2026-01-01T00:00:00Z") as frozen:
            authenticator = GithubAppMultiPemAuthenticator(
                config={}, parameters={}, github_apps=_github_apps_field(("111", "222", FAKE_PEM))
            )
            authenticator._ensure_ready()
            cache = authenticator._caches[0]
            assert cache.get_token() == "ghs_first"
            frozen.tick(delta=__import__("datetime").timedelta(hours=1, minutes=1))
            assert cache.get_token() == "ghs_second"

    def test_bad_credentials_raise_traced_config_error(self, requests_mock):
        requests_mock.post(_access_token_url("222"), status_code=401, json={"message": "Bad credentials"})
        authenticator = GithubAppMultiPemAuthenticator(config={}, parameters={}, github_apps=_github_apps_field(("111", "222", FAKE_PEM)))
        with pytest.raises(AirbyteTracedException) as exc_info:
            authenticator.token  # construction itself must never raise — see test_manifest_selective_authenticator_builds_in_token_mode
        assert exc_info.value.failure_type == FailureType.config_error


class TestStickyRotation:
    def test_stays_on_active_installation_while_it_has_quota(self, requests_mock):
        requests_mock.post(_access_token_url("222"), json={"token": "ghs_a"})
        requests_mock.post(_access_token_url("444"), json={"token": "ghs_b"})
        requests_mock.get(
            "https://api.github.com/rate_limit",
            [
                {"json": {"resources": {"core": {"remaining": 500, "reset": 4070908800}}}},
                {"json": {"resources": {"core": {"remaining": 500, "reset": 4070908800}}}},
            ],
        )
        authenticator = GithubAppMultiPemAuthenticator(
            config={}, parameters={}, github_apps=_github_apps_field(("111", "222", FAKE_PEM), ("333", "444", FAKE_PEM))
        )
        assert authenticator.token == "token ghs_a"
        assert authenticator.token == "token ghs_a"
        assert authenticator.token == "token ghs_a"

    def test_rotates_once_active_drops_into_reserve(self, requests_mock):
        requests_mock.post(_access_token_url("222"), json={"token": "ghs_a"})
        requests_mock.post(_access_token_url("444"), json={"token": "ghs_b"})
        requests_mock.get(
            "https://api.github.com/rate_limit",
            [
                {"json": {"resources": {"core": {"remaining": 51, "reset": 4070908800}}}},
                {"json": {"resources": {"core": {"remaining": 500, "reset": 4070908800}}}},
            ],
        )
        authenticator = GithubAppMultiPemAuthenticator(
            config={}, parameters={}, github_apps=_github_apps_field(("111", "222", FAKE_PEM), ("333", "444", FAKE_PEM))
        )
        assert authenticator.token == "token ghs_a"  # remaining 51 -> 50, still above reserve check next time? no: 50 is not > 50
        assert authenticator.token == "token ghs_b"  # cache 0 now at 50, not > _BUDGET_MIN_RESERVE (50), rotates

    def test_cascades_through_four_installations(self, requests_mock):
        """The rotation logic (`n = len(self._caches)`, generic loop) is written for any N, but
        every other test here only exercises N=2. This confirms it actually cascades correctly
        across more than two — install 1/2/3 each have just enough quota for one call before
        dropping into reserve, install 4 has plenty, so the sequence should visit all four in
        order and then stay on the fourth.
        """
        for installation_id, token in (("222", "ghs_a"), ("444", "ghs_b"), ("666", "ghs_c"), ("888", "ghs_d")):
            requests_mock.post(_access_token_url(installation_id), json={"token": token})
        requests_mock.get(
            "https://api.github.com/rate_limit",
            [
                {"json": {"resources": {"core": {"remaining": 51, "reset": 4070908800}}}},
                {"json": {"resources": {"core": {"remaining": 51, "reset": 4070908800}}}},
                {"json": {"resources": {"core": {"remaining": 51, "reset": 4070908800}}}},
                {"json": {"resources": {"core": {"remaining": 500, "reset": 4070908800}}}},
            ],
        )
        authenticator = GithubAppMultiPemAuthenticator(
            config={},
            parameters={},
            github_apps=_github_apps_field(
                ("111", "222", FAKE_PEM), ("333", "444", FAKE_PEM), ("555", "666", FAKE_PEM), ("777", "888", FAKE_PEM)
            ),
        )
        assert [authenticator.token for _ in range(5)] == [
            "token ghs_a",
            "token ghs_b",
            "token ghs_c",
            "token ghs_d",
            "token ghs_d",  # install 4 has plenty of quota (500 -> 499), stays put
        ]

    def test_all_exhausted_sleeps_until_earliest_reset_then_reseeds(self, requests_mock, monkeypatch):
        requests_mock.post(_access_token_url("222"), json={"token": "ghs_a"})
        requests_mock.post(_access_token_url("444"), json={"token": "ghs_b"})
        requests_mock.get(
            "https://api.github.com/rate_limit",
            [
                {"json": {"resources": {"core": {"remaining": 0, "reset": 1000}}}},
                {"json": {"resources": {"core": {"remaining": 0, "reset": 2000}}}},
                {"json": {"resources": {"core": {"remaining": 5000, "reset": 4070908800}}}},
                {"json": {"resources": {"core": {"remaining": 5000, "reset": 4070908800}}}},
            ],
        )
        sleeps = []
        monkeypatch.setattr("components.time.sleep", lambda seconds: sleeps.append(seconds))
        monkeypatch.setattr("components.time.time", lambda: 999.0)
        authenticator = GithubAppMultiPemAuthenticator(
            config={}, parameters={}, github_apps=_github_apps_field(("111", "222", FAKE_PEM), ("333", "444", FAKE_PEM))
        )
        token = authenticator.token
        assert token in ("token ghs_a", "token ghs_b")
        assert sleeps == [1.0]  # earliest reset (1000) minus frozen "now" (999)


class TestMintAppJwtErrors:
    def test_malformed_private_key_raises_traced_config_error(self, monkeypatch):
        # Override the module-level autouse stub for this test only, so `_mint_app_jwt` exercises
        # the real PyJWT/cryptography failure it is meant to wrap.
        monkeypatch.setattr("components.jwt.encode", _REAL_JWT_ENCODE)
        cache = _InstallationTokenCache(app_id="111", installation_id="222", private_key="not a real pem")
        with pytest.raises(AirbyteTracedException) as exc_info:
            cache._mint_app_jwt()
        assert exc_info.value.failure_type == FailureType.config_error
        # The underlying library error is reported, but never the key material itself.
        assert "not a real pem" not in exc_info.value.internal_message
        assert "not a real pem" not in exc_info.value.message


class TestConcurrency:
    def test_concurrent_token_calls_do_not_lose_decrements(self, requests_mock):
        """Regression test for the sticky-rotation state (`_active_index` and each cache's
        `remaining`) being read/decremented under a lock. Without it, concurrent threads racing
        the check-then-decrement could both act on a stale `remaining` value and lose updates —
        this pins the counter to exactly `seeded - total_calls` after every thread finishes.
        """
        requests_mock.post(_access_token_url("222"), json={"token": "ghs_a"})
        n_threads, calls_per_thread = 20, 25
        total_calls = n_threads * calls_per_thread
        seeded = total_calls + 1000  # comfortably above the reserve for the whole run: no rotation/waits involved
        requests_mock.get("https://api.github.com/rate_limit", json={"resources": {"core": {"remaining": seeded, "reset": 4070908800}}})
        authenticator = GithubAppMultiPemAuthenticator(config={}, parameters={}, github_apps=_github_apps_field(("111", "222", FAKE_PEM)))

        barrier = threading.Barrier(n_threads)

        def worker():
            barrier.wait()
            for _ in range(calls_per_thread):
                authenticator.token

        threads = [threading.Thread(target=worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert authenticator._caches[0].remaining == seeded - total_calls

    def test_concurrent_first_use_seeds_quota_once(self, requests_mock):
        """Regression test for double-checked locking in `_ensure_ready`: concurrent first calls
        to `.token` must parse `github_apps` and seed quota exactly once, not once per thread.
        """
        requests_mock.post(_access_token_url("222"), json={"token": "ghs_a"})
        rate_limit_mock = requests_mock.get(
            "https://api.github.com/rate_limit", json={"resources": {"core": {"remaining": 5000, "reset": 4070908800}}}
        )
        authenticator = GithubAppMultiPemAuthenticator(config={}, parameters={}, github_apps=_github_apps_field(("111", "222", FAKE_PEM)))

        n_threads = 10
        barrier = threading.Barrier(n_threads)

        def worker():
            barrier.wait()
            authenticator.token

        threads = [threading.Thread(target=worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert rate_limit_mock.call_count == 1


class TestAuthMode:
    @pytest.mark.parametrize(
        "config, expected",
        [
            pytest.param({"credentials": {"github_apps": "111"}}, "github_apps", id="github_apps"),
            pytest.param({"credentials": {"personal_access_token": "pat-token"}}, "token", id="pat"),
            pytest.param(
                {"credentials": {"access_token": "oauth-token", "client_id": "id", "client_secret": "secret"}}, "token", id="oauth"
            ),
            pytest.param({"access_token": "legacy-token"}, "token", id="legacy_root_access_token"),
        ],
    )
    def test_config_normalization_sets_auth_mode(self, config, expected):
        ConfigNormalization().transform(config)
        assert config["credentials"]["auth_mode"] == expected


class TestManifestSelectiveAuthenticator:
    """`ModelToComponentFactory.create_selective_authenticator` builds every branch eagerly, so
    each mode must construct with the other branch's credentials absent."""

    def _build(self, config):
        source = make_source(config=config)
        return source._constructor.create_component(
            model_type=SelectiveAuthenticatorModel,
            component_definition=source.resolved_manifest["definitions"]["requester_base"]["authenticator"],
            config=source._config,
        )

    def test_github_apps_mode(self, requests_mock):
        requests_mock.post(_access_token_url("222"), json={"token": "ghs_a"})
        requests_mock.get("https://api.github.com/rate_limit", json={"resources": {"core": {"remaining": 5000, "reset": 4070908800}}})
        authenticator = self._build(
            {"credentials": {"github_apps": _github_apps_field(("111", "222", FAKE_PEM))}, "repositories": ["org/repo"]}
        )
        assert isinstance(authenticator, GithubAppMultiPemAuthenticator)
        assert authenticator.token == "token ghs_a"

    @pytest.mark.parametrize(
        "credentials_config",
        [
            pytest.param({"access_token": "pat-token"}, id="legacy_root_access_token"),
            pytest.param({"credentials": {"access_token": "oauth-token", "client_id": "id", "client_secret": "secret"}}, id="oauth"),
            pytest.param({"credentials": {"personal_access_token": "pat-token"}}, id="pat"),
        ],
    )
    def test_token_mode(self, credentials_config, rate_limit_mock_response):
        authenticator = self._build({**credentials_config, "repositories": ["org/repo"]})
        assert isinstance(authenticator, RateLimitedMultipleTokenAuthenticator)
