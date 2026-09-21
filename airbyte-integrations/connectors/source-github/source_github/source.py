#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    ConfiguredAirbyteCatalog,
    FailureType,
    Status,
)
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    RateLimitedMultipleTokenAuthenticator as RateLimitedMultipleTokenAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    UnionPartitionRouter as UnionPartitionRouterModel,
)
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from . import constants


class SourceGithub(YamlDeclarativeSource):
    def __init__(
        self,
        catalog: Optional[ConfiguredAirbyteCatalog] = None,
        config: Optional[Mapping[str, Any]] = None,
        state: Optional[TState] = None,
    ) -> None:
        super().__init__(catalog=catalog, config=config, state=state, path_to_yaml="manifest.yaml")

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        check_succeeded, error = self.check_connection(logger, config)
        if not check_succeeded:
            return AirbyteConnectionStatus(status=Status.FAILED, message=repr(error))
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def _resolve_repositories_and_organizations(self, config: Mapping[str, Any]) -> Tuple[List[str], List[str]]:
        """Resolve wildcard patterns and explicit repos by enumerating the manifest's
        partition routers — the same components manifest streams slice on at read
        time, so the resolution sees the same repository list.

        Wildcard patterns (`org/*`, `org/prefix*`) expand via `repositories_resolver`;
        explicit `org/repo` entries validate via `repository_stats`; entries that 404
        are skipped with a warning (see `requester_base`'s error_handler in the
        manifest). User-owned repos contribute a repository but no organization.
        The resolver streams' `use_cache: true` means this enumeration warms the HTTP
        cache the manifest streams reuse when reading.

        Organizations come from `organization_resolution_partition_router` — payload-
        confirmed logins only — which is deliberately narrower than the
        `organization_partition_router` the `repositories` stream slices on; see that
        definition's comment in the manifest.

        Returns (organizations, repositories), both sorted and deduplicated.
        """
        try:
            _, token = self.get_access_token(config)
        except Exception:
            token = ""
        if not any(t.strip() for t in (token or "").split(constants.TOKEN_SEPARATOR)):
            raise AirbyteTracedException(
                message="No authentication tokens found in config.",
                failure_type=FailureType.config_error,
            )

        def enumerate_router(definition_name: str, partition_key: str) -> List[str]:
            router = self._constructor.create_component(
                model_type=UnionPartitionRouterModel,
                component_definition=self.resolved_manifest["definitions"][definition_name],
                config=config,
                stream_name=f"{partition_key}_resolution",
            )
            return sorted({stream_slice.partition[partition_key] for stream_slice in router.stream_slices()})

        repositories = enumerate_router("repository_partition_router", "repository")
        # `organization_resolution_partition_router`, not `organization_partition_router`: a
        # login that config only *claims* is an org must never reach the org-scoped streams.
        # Config-derived orgs put a user login on `Organizations`, `Teams` and `Users`, where
        # `orgs/{user}` 404s on every request. The `in repository_owners` filter is a backstop:
        # an org owning no resolved repository has nothing to sync.
        repository_owners = {repository.split("/", 1)[0] for repository in repositories}
        organizations = [
            organization
            for organization in enumerate_router("organization_resolution_partition_router", "organization")
            if organization in repository_owners
        ]
        return organizations, repositories

    @staticmethod
    def get_access_token(config: Mapping[str, Any]):
        # Before we supported oauth, personal_access_token was called `access_token` and it lived at the
        # config root. So we first check to make sure any backwards compatbility is handled.
        if "access_token" in config:
            return constants.PERSONAL_ACCESS_TOKEN_TITLE, config["access_token"]

        credentials = config.get("credentials", {})
        if "access_token" in credentials:
            return constants.ACCESS_TOKEN_TITLE, credentials["access_token"]
        if "personal_access_token" in credentials:
            return constants.PERSONAL_ACCESS_TOKEN_TITLE, credentials["personal_access_token"]
        raise Exception("Invalid config format")

    def _get_authenticator(self, config: Mapping[str, Any]) -> DeclarativeAuthenticator:
        """Return the manifest's `RateLimitedMultipleTokenAuthenticator` so the repository
        resolution requests charge the same per-token quota counters as the streams.

        This does NOT build a second authenticator, even though it reads like it: the CDK's
        `ModelToComponentFactory` caches `RateLimitedMultipleTokenAuthenticator` instances in
        `self._rate_limited_authenticators`, keyed by their *resolved* constructor arguments,
        precisely so that every stream shares one set of quota counters (the same mechanism
        `api_budget` uses). Since `self._constructor` is the very factory that builds the
        manifest streams, the call below returns the instance already bound to their
        requesters — verified by `test_authenticator_instance_is_shared_with_manifest_streams`.

        Because the cache key is value-based, a *differently resolved* config yields a
        different instance. Two consequences worth knowing:
          - `config` must be normalized — the config the source was constructed with, or one
            run through `_spec_component.transform_config` — so `api_url` is defaulted;
          - `check_connection` intentionally resolves with `max_waiting_time: 0`, which is a
            separate instance by design.
        """
        return self._constructor.create_component(
            model_type=RateLimitedMultipleTokenAuthenticatorModel,
            component_definition=self.resolved_manifest["definitions"]["requester_base"]["authenticator"],
            config=config,
        )

    def user_friendly_error_message(self, message: str) -> str:
        # The two 404 branches this helper used to carry — "Repo name X is unknown" and
        # "Organization name X is unknown" — are gone because nothing can reach them any more:
        # repository resolution is declarative, and the manifest's shared error handler maps 404
        # to IGNORE (skip the org/repo with a warning), so no 404 is ever raised for this helper
        # to rewrite. `check_connection` reports the generic "couldn't be found" message for
        # that case instead. The 401 branch below is still reached, via the quota-status request.
        user_message = ""
        if "401 Client Error: Unauthorized for url" in message or ("Error: Unauthorized" in message and "401" in message):
            user_message = (
                "GitHub authentication failed (HTTP 401). Please verify your Personal Access Token or OAuth credentials "
                "are valid and not expired."
            )
        return user_message

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        # `check` is handed the raw file config, so apply the manifest spec's normalization
        # and validation here — the same rules read/discover get from the spec.
        config = dict(config)
        self._spec_component.transform_config(config)
        self._spec_component.validate_config(config)
        # `check` is interactive and must answer in seconds, so it resolves with the smallest
        # budget the spec allows. This replaces the deleted `exit_on_rate_limit = True if
        # is_check_connection else False`: "PT1M" makes
        # RateLimitedMultipleTokenAuthenticator._acquire_call raise "Rate limit is exceeded for
        # all provided tokens." on an exhausted quota instead of sleeping up to
        # `max_waiting_time` (120 minutes by default), which the platform would surface as an
        # opaque timeout. `streams()` keeps the user-configured value, so sync-time waiting is
        # unchanged.
        #
        # 1 rather than 0: the manifest's backoff caps resolve to `max_waiting_time * 60 + 1`,
        # and `WaitUntilTimeFromHeader` returns its `min_wait: 60` floor for *every* retryable
        # response that carries no rate-limit header — a 500, a 429 without headers, a
        # connection timeout. A cap of 1s refuses that floor, so one transient GitHub error
        # failed `check` on the first attempt with the rate-limit message. 61s is above the
        # floor and far below the distance to any real GitHub reset, so both fail-fast paths
        # are unchanged and a blip is retried instead.
        check_config = {**config, "max_waiting_time": 1}
        try:
            _, repositories = self._resolve_repositories_and_organizations(check_config)
            if not repositories:
                return (
                    False,
                    "Some of the provided repositories couldn't be found. Please verify if every entered repository has a valid name and it matches the following format: airbytehq/airbyte airbytehq/another-repo airbytehq/* airbytehq/airbyte.",
                )
            return True, None

        except AirbyteTracedException as e:
            user_message = self.user_friendly_error_message(e.message)
            return False, user_message or e.message
        except Exception as e:
            message = repr(e)
            user_message = self.user_friendly_error_message(message)
            return False, user_message or message
