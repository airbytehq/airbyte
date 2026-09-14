#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
import threading
import time
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Tuple, Union

import jwt
import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.utils import AirbyteTracedException


logger = logging.getLogger("airbyte")

# GitHub always issues installation access tokens valid for exactly 1 hour; refresh a bit early so
# a token already handed to an in-flight request is never right at the edge of expiry.
_REFRESH_MARGIN_SECONDS = 120
_INSTALLATION_TOKEN_LIFETIME_SECONDS = 3600

# Same constants as the PAT path's sticky-token behavior (MultipleTokenAuthenticatorWithRateLimiter):
# stick with an installation until its tracked quota drops into this reserve, then rotate.
_BUDGET_MIN_RESERVE = 50
_MAX_WAIT_SECONDS = 60 * 120


class _InstallationTokenCache:
    """Mints and caches one GitHub App installation's access token, refreshing it on demand, and
    tracks that installation's REST rate-limit quota so the authenticator can stick with it until
    exhausted (mirroring the PAT path) instead of blindly round-robining every call.

    Token refresh happens lazily on the next `get_token()` call once the cached token is close to
    expiry — not once at sync startup — so a sync that runs for many hours never ends up making
    calls with a token that died partway through.
    """

    def __init__(self, app_id: str, installation_id: str, private_key: str) -> None:
        self._app_id = app_id
        self._installation_id = installation_id
        self._private_key = private_key
        self._token: Optional[str] = None
        self._expires_at: float = 0.0
        self.remaining: Optional[int] = None
        self.reset_at: Optional[float] = None
        # Guards `_token`/`_expires_at`: `get_token()` can be called concurrently for the same
        # installation (multiple in-flight partition reads sharing one authenticator), and without
        # this a race between the expiry check and the refresh could mint the token twice at once.
        self._token_lock = threading.Lock()

    def _mint_app_jwt(self) -> str:
        now = int(time.time())
        payload = {"iat": now - 60, "exp": now + 540, "iss": self._app_id}
        try:
            return jwt.encode(payload, self._private_key, algorithm="RS256")
        except Exception as e:
            # A malformed/garbage PEM surfaces here (e.g. PyJWT/cryptography's
            # "Could not deserialize key data..."). Wrap it the same way the installation-token
            # exchange's 401/403/404 are wrapped below, instead of letting a raw library
            # exception reach the user with no actionable guidance. Neither that exception nor
            # this message ever includes the key material itself.
            raise AirbyteTracedException(
                message=f"GitHub App authentication failed. The private key for app_id '{self._app_id}' could not be used to "
                "sign a JWT — please verify it is a valid, unencrypted PEM-formatted RSA private key.",
                internal_message=f"Failed to sign the GitHub App JWT for app_id={self._app_id}: {e}",
                failure_type=FailureType.config_error,
            ) from e

    def _refresh_token(self) -> None:
        response = requests.post(
            f"https://api.github.com/app/installations/{self._installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {self._mint_app_jwt()}",
                "Accept": "application/vnd.github+json",
            },
            timeout=30,
        )
        if response.status_code in (401, 403, 404):
            raise AirbyteTracedException(
                message="GitHub App authentication failed. Please verify the app_id, installation_id and private key are correct.",
                internal_message=f"Installation token exchange failed for app_id={self._app_id}: {response.status_code} {response.text}",
                failure_type=FailureType.config_error,
            )
        response.raise_for_status()
        self._token = response.json()["token"]
        self._expires_at = time.time() + _INSTALLATION_TOKEN_LIFETIME_SECONDS - _REFRESH_MARGIN_SECONDS
        logger.info(
            "github_app_auth: minted installation token (app_id=%s, installation_id=%s, expires_at=%s)",
            self._app_id,
            self._installation_id,
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self._expires_at)),
        )

    def get_token(self) -> str:
        if self._token is None or time.time() >= self._expires_at:
            with self._token_lock:
                # Re-check inside the lock: another thread may have refreshed while this one
                # was waiting to acquire it, in which case minting again would be redundant.
                if self._token is None or time.time() >= self._expires_at:
                    self._refresh_token()
        return self._token  # type: ignore[return-value]

    def refresh_quota(self) -> None:
        """Seed `remaining`/`reset_at` from GitHub's own accounting for this installation."""
        response = requests.get(
            "https://api.github.com/rate_limit",
            headers={"Authorization": f"token {self.get_token()}", "Accept": "application/vnd.github+json"},
            timeout=30,
        )
        response.raise_for_status()
        core = response.json()["resources"]["core"]
        self.remaining = core["remaining"]
        self.reset_at = core["reset"]


def _parse_entries(github_apps: str) -> List[Tuple[str, str, str]]:
    """Parses repeated {app_id line}\\n{installation_id line}\\n{PEM block} groups, blank lines
    between groups allowed. The PEM block is taken verbatim from its `-----BEGIN` line through
    its `-----END` line, so a real .pem file can be pasted as-is.
    """
    lines = github_apps.splitlines()
    n = len(lines)
    entries: List[Tuple[str, str, str]] = []
    i = 0

    def next_nonblank(i: int) -> int:
        while i < n and not lines[i].strip():
            i += 1
        return i

    while True:
        i = next_nonblank(i)
        if i >= n:
            break
        app_id = lines[i].strip()
        i = next_nonblank(i + 1)
        if i >= n:
            raise ValueError(f"credentials.github_apps: missing installation_id after app_id '{app_id}'")
        installation_id = lines[i].strip()
        i = next_nonblank(i + 1)
        if i >= n or not lines[i].strip().startswith("-----BEGIN"):
            raise ValueError(f"credentials.github_apps: expected a '-----BEGIN...' PEM block after installation_id '{installation_id}'")
        pem_lines = []
        found_end = False
        while i < n:
            pem_lines.append(lines[i])
            if lines[i].strip().startswith("-----END"):
                i += 1
                found_end = True
                break
            i += 1
        if not found_end:
            raise ValueError(f"credentials.github_apps: PEM block for app_id '{app_id}' never reached a '-----END...' line")
        entries.append((app_id, installation_id, "\n".join(pem_lines)))
    return entries


@dataclass
class GithubAppMultiPemAuthenticator(DeclarativeAuthenticator):
    """
    Authenticates as one or more GitHub App installations from a single config field
    (`credentials.github_apps`): repeated groups of app_id line, installation_id line, then the
    private key .pem pasted as-is (`-----BEGIN...` through `-----END...`) — repeat for more
    installations, blank lines between groups are fine.

    Each entry gets its own installation-token cache, minted and refreshed independently and
    lazily — never all at once at startup — which is what lets a single sync outlive any one
    token's ~1h lifetime.

    With multiple entries, mirrors the PAT path's sticky-until-exhausted rotation
    (`MultipleTokenAuthenticatorWithRateLimiter`/`RateLimitedMultipleTokenAuthenticator`) instead
    of blindly round-robining every call: stays on one installation while it has quota, rotates
    to the next once it drops into the reserve, and waits out the earliest reset if all are
    exhausted.
    """

    config: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]]
    github_apps: Union[InterpolatedString, str]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        # Parsing only — no validation, no network calls. `ModelToComponentFactory
        # .create_selective_authenticator` builds every branch under `authenticators:` eagerly,
        # not just the selected one, so this constructor also runs when the config is in "token"
        # mode and `github_apps` is empty. Raising here (or seeding quota, which would need a
        # real token) would break every PAT/OAuth user. Both are deferred to first actual use
        # in `_ensure_ready`, which only happens if this branch is the one truly selected.
        self._parameters = parameters
        self._caches: Optional[List[_InstallationTokenCache]] = None
        self._active_index = 0
        # Guards `_caches`/`_active_index` and every cache's `remaining` counter.
        # `ConcurrentDeclarativeSource` can read multiple partition streams in parallel, all
        # sharing this one authenticator instance (mirroring `RateLimitedMultipleTokenAuthenticator`,
        # which documents the same requirement) — without a lock, two threads racing the
        # check-then-decrement in `_next_available_cache`/`token` could both pick an already
        # exhausted cache, or step on each other's rotation of `_active_index`. Sleeping while
        # waiting out an exhaustion window happens outside the lock so one thread's wait never
        # blocks another from making progress.
        self._lock = threading.Lock()

    def _ensure_ready(self) -> None:
        if self._caches is not None:
            return
        with self._lock:
            if self._caches is not None:
                return
            github_apps_value = InterpolatedString.create(self.github_apps, parameters=self._parameters).eval(self.config)
            entries = _parse_entries(github_apps_value) if github_apps_value else []
            if not entries:
                raise ValueError("credentials.github_apps must have at least one app_id/installation_id/PEM group")
            caches = [_InstallationTokenCache(app_id, installation_id, private_key) for app_id, installation_id, private_key in entries]
            for cache in caches:
                cache.refresh_quota()
            self._caches = caches

    def _select_cache_locked(self) -> Optional[_InstallationTokenCache]:
        """Must be called while holding `self._lock`. Returns the active cache with its
        `remaining` counter already decremented, or `None` if every cache is exhausted."""
        n = len(self._caches)
        for _ in range(n):
            cache = self._caches[self._active_index]
            if cache.remaining is None or cache.remaining > _BUDGET_MIN_RESERVE:
                if cache.remaining is not None:
                    cache.remaining -= 1
                return cache
            self._active_index = (self._active_index + 1) % n
        return None

    def _next_available_cache(self) -> _InstallationTokenCache:
        self._ensure_ready()
        while True:
            with self._lock:
                cache = self._select_cache_locked()
                if cache is not None:
                    return cache
                wait_seconds = max(0.0, min(c.reset_at for c in self._caches) - time.time())

            if wait_seconds > _MAX_WAIT_SECONDS:
                raise AirbyteTracedException(
                    message="Rate limit exceeded for all configured GitHub App installations.",
                    failure_type=FailureType.transient_error,
                )
            logger.info("github_app_auth: all installations exhausted, sleeping %.0fs until the earliest reset", wait_seconds)
            time.sleep(wait_seconds)
            for cache in self._caches:
                cache.refresh_quota()

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        cache = self._next_available_cache()
        return f"token {cache.get_token()}"
