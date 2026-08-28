#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from os import getenv
from typing import Any, Iterator, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urlparse

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    FailureType,
    Status,
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    RateLimitedMultipleTokenAuthenticator as RateLimitedMultipleTokenAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    UnionPartitionRouter as UnionPartitionRouterModel,
)
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from . import constants
from .streams import (
    Assignees,
    Branches,
    Collaborators,
    Comments,
    CommitCommentReactions,
    CommitComments,
    Commits,
    ContributorActivity,
    Deployments,
    Events,
    IssueCommentReactions,
    IssueEvents,
    IssueLabels,
    IssueMilestones,
    IssueReactions,
    Issues,
    IssueTimelineEvents,
    Organizations,
    ProjectCards,
    ProjectColumns,
    Projects,
    ProjectsV2,
    PullRequestCommentReactions,
    PullRequestCommits,
    PullRequests,
    PullRequestStats,
    Releases,
    ReviewComments,
    Reviews,
    Stargazers,
    Tags,
    TeamMembers,
    TeamMemberships,
    Teams,
    Users,
    WorkflowJobs,
    WorkflowRuns,
    Workflows,
)


class SourceGithub(YamlDeclarativeSource, AbstractSource):
    continue_sync_on_stream_failure = True

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

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[List[AirbyteStateMessage]] = None,
    ) -> Iterator[AirbyteMessage]:
        """Route manifest streams to `ConcurrentDeclarativeSource` and Python streams to `AbstractSource`.

        CDK v7 removed the `_group_streams` mechanism that CDK v6 had. This override
        replicates that behavior: manifest-backed `AbstractStream` objects are read
        concurrently, while regular Python `Stream` objects are read through
        `AbstractSource.read()`.

        The config is validated and transformed up front so that manifest streams see
        normalized keys (legacy `repository`/`branch` converted to arrays, `api_url`
        defaulted). Repository/organization resolution for the Python streams happens
        lazily inside `streams()` by enumerating the manifest's shared partition
        routers, so manifest-only catalogs skip it entirely. As streams are migrated
        from Python to the manifest, they automatically move from the synchronous to
        the concurrent path.
        """
        effective_config = self._validate_and_transform_config(self._config or config)
        self._sync_manifest_config(effective_config)
        concurrent_streams = super().streams(config=effective_config)
        concurrent_stream_names = {stream.name for stream in concurrent_streams}

        concurrent_catalog = ConfiguredAirbyteCatalog(streams=[s for s in catalog.streams if s.stream.name in concurrent_stream_names])
        if concurrent_catalog.streams:
            selected = self._select_streams(streams=concurrent_streams, configured_catalog=concurrent_catalog)
            if selected:
                yield from self._concurrent_source.read(selected)

        synchronous_catalog = ConfiguredAirbyteCatalog(streams=[s for s in catalog.streams if s.stream.name not in concurrent_stream_names])
        if synchronous_catalog.streams:
            # Pass effective_config (not the raw config) so streams() sees the
            # normalized keys (repositories array, api_url default) when
            # AbstractSource.read re-enters it.
            yield from AbstractSource.read(self, logger, effective_config, synchronous_catalog, state)

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Return the union of Python `Stream` objects and manifest-backed streams.

        `ConcurrentDeclarativeSource.discover()` only reports manifest streams, so this
        override adds the Python streams from `SourceGithub.streams()`. As streams move
        into the manifest they leave the Python list and are reported via
        `super().streams()`, keeping the discovered catalog complete throughout the migration.
        """
        effective_config = self._config or config
        streams = [stream.as_airbyte_stream() for stream in self.streams(config=effective_config)]
        streams += [stream.as_airbyte_stream() for stream in super().streams(config=effective_config)]
        return AirbyteCatalog(streams=streams)

    def _resolve_repositories_and_organizations(self, config: Mapping[str, Any]) -> Tuple[List[str], List[str]]:
        """Resolve wildcard patterns and explicit repos by enumerating the manifest's
        shared partition routers — the same components manifest streams slice on at
        read time, so the Python streams are guaranteed to see identical lists.

        Wildcard patterns (`org/*`, `org/prefix*`) expand via `repositories_resolver`;
        explicit `org/repo` entries validate via `repository_stats`; entries that 404
        are skipped with a warning (see `requester_base`'s error_handler in the
        manifest). User-owned repos contribute a repository but no organization.
        The resolver streams' `use_cache: true` means this enumeration warms the HTTP
        cache the manifest streams reuse when reading.

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
        # The organization router unions config-derived wildcard orgs with the orgs
        # owning explicit repos, so a wildcard entry whose org doesn't exist (404) or
        # matched no repos would still yield a partition. Keep only orgs that own at
        # least one resolved repository — the legacy resolver derived orgs from
        # fetched repo metadata, so orgs without any synced repo never surfaced.
        repository_owners = {repository.split("/", 1)[0] for repository in repositories}
        organizations = [
            organization
            for organization in enumerate_router("organization_partition_router", "organization")
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
        """Return the manifest's `RateLimitedMultipleTokenAuthenticator` so the Python streams
        charge the same per-token quota counters as the declarative ones.

        This does NOT build a second authenticator, even though it reads like it: the CDK's
        `ModelToComponentFactory` caches `RateLimitedMultipleTokenAuthenticator` instances in
        `self._rate_limited_authenticators`, keyed by their *resolved* constructor arguments,
        precisely so that every stream shares one set of quota counters (the same mechanism
        `api_budget` uses). Since `self._constructor` is the very factory that builds the
        manifest streams, the call below returns the instance already bound to their
        requesters — verified by `test_authenticator_instance_is_shared_with_manifest_streams`.

        Because the cache key is value-based, a *differently resolved* config yields a
        different instance. Two consequences worth knowing:
          - `config` must be the transformed config (normalized `api_url`), so this is called
            after `_validate_and_transform_config`;
          - `check_connection` intentionally resolves with `max_waiting_time: 0`, which is a
            separate instance by design — `check` builds no Python streams.
        """
        return self._constructor.create_component(
            model_type=RateLimitedMultipleTokenAuthenticatorModel,
            component_definition=self.resolved_manifest["definitions"]["requester_base"]["authenticator"],
            config=config,
        )

    def _sync_manifest_config(self, config: Mapping[str, Any]) -> None:
        """Push the transformed config into `self._config`, which manifest components read.

        `ConcurrentDeclarativeSource.streams()` ignores its `config` argument and interpolates
        from `self._config` (concurrent_declarative_source.py), so a config normalized here —
        `api_url` defaulted, legacy `repository`/`branch` converted to arrays — would otherwise
        never reach the manifest streams. Both entry points that transform the config call
        this, so the two copies of the assignment cannot drift apart.

        TODO: drop once the CDK lets a source hand `streams()` its own config.
        """
        if isinstance(self._config, dict):
            self._config.update(config)

    def _validate_and_transform_config(self, config: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        config = self._ensure_default_values(config)
        config = self._validate_repositories(config)
        config = self._validate_branches(config)
        return config

    def _ensure_default_values(self, config: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        # `not config.get(...)` rather than `setdefault`: the key can be present and null or
        # empty — null via the API or Terraform, empty because the spec tells users to "leave it
        # empty to use GitHub" — and both used to reach `urlparse` as a non-string, crashing with
        # an unhandled TypeError/AttributeError where every other bad `api_url` gets an
        # actionable config error.
        if not config.get("api_url"):
            config["api_url"] = "https://api.github.com"
        if not config["api_url"].endswith("/"):
            config["api_url"] = config["api_url"] + "/"
        api_url_parsed = urlparse(config["api_url"])

        if not api_url_parsed.scheme.startswith("http"):
            message = "Please enter a full url for `API URL` field starting with `http`"
        elif api_url_parsed.scheme == "http" and not self._is_http_allowed():
            message = "HTTP connection is insecure and is not allowed in this environment. Please use `https` instead."
        elif not api_url_parsed.netloc:
            message = "Please provide a correct API URL."
        else:
            return config

        raise AirbyteTracedException(message=message, failure_type=FailureType.config_error)

    def _validate_repositories(self, config: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        if config.get("repositories"):
            pass
        elif config.get("repository"):
            config["repositories"] = set(filter(None, config["repository"].split(" ")))

        return config

    def _validate_branches(self, config: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        if config.get("branches"):
            pass
        elif config.get("branch"):
            config["branches"] = set(filter(None, config["branch"].split(" ")))

        return config

    @staticmethod
    def _is_http_allowed() -> bool:
        return getenv("DEPLOYMENT_MODE", "").upper() != "CLOUD"

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
        config = self._validate_and_transform_config(config)
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

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self._validate_and_transform_config(config)
        # Resolved after the transform so the authenticator's `quota_status_url` is built from
        # the normalized `api_url` — see `_get_authenticator` on why that matters for sharing.
        authenticator = self._get_authenticator(config)

        organizations, repositories = self._resolve_repositories_and_organizations(config)

        if not any((organizations, repositories)):
            user_message = (
                "No streams available. Looks like your config for repositories or organizations is not valid."
                " Please, check your permissions, names of repositories and organizations."
                " Needed scopes: repo, read:org, read:repo_hook, read:user, read:discussion, workflow."
            )
            raise AirbyteTracedException(
                internal_message="No streams available. Please check permissions",
                message=user_message,
                failure_type=FailureType.config_error,
            )

        # This parameter is deprecated and in future will be used sane default, page_size: 10
        page_size = config.get("page_size_for_large_streams", constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM)
        access_token_type, _ = self.get_access_token(config)
        max_wait_time_seconds = (config["max_waiting_time"] if config.get("max_waiting_time") is not None else 120) * 60
        organization_args = {
            "authenticator": authenticator,
            "organizations": organizations,
            "api_url": config.get("api_url"),
            "access_token_type": access_token_type,
            "max_wait_time_seconds": max_wait_time_seconds,
        }
        start_date = config.get("start_date")

        repository_args = {
            "authenticator": authenticator,
            "api_url": config.get("api_url"),
            "repositories": repositories,
            "page_size_for_large_streams": page_size,
            "access_token_type": access_token_type,
            "max_wait_time_seconds": max_wait_time_seconds,
        }
        repository_args_with_start_date = {**repository_args, "start_date": start_date}

        pull_requests_stream = PullRequests(**repository_args_with_start_date)
        projects_stream = Projects(**repository_args_with_start_date)
        project_columns_stream = ProjectColumns(projects_stream, **repository_args_with_start_date)
        teams_stream = Teams(**organization_args)
        team_members_stream = TeamMembers(parent=teams_stream, **repository_args)
        workflow_runs_stream = WorkflowRuns(**repository_args_with_start_date)

        self._sync_manifest_config(config)

        python_streams = [
            IssueTimelineEvents(**repository_args),
            Assignees(**repository_args),
            Branches(**repository_args),
            Collaborators(**repository_args),
            Comments(**repository_args_with_start_date),
            CommitCommentReactions(**repository_args_with_start_date),
            CommitComments(**repository_args_with_start_date),
            Commits(**repository_args_with_start_date, branches_to_pull=config.get("branches", [])),
            ContributorActivity(**repository_args),
            Deployments(**repository_args_with_start_date),
            Events(**repository_args_with_start_date),
            IssueCommentReactions(**repository_args_with_start_date),
            IssueEvents(**repository_args_with_start_date),
            IssueLabels(**repository_args),
            IssueMilestones(**repository_args_with_start_date),
            IssueReactions(**repository_args_with_start_date),
            Issues(**repository_args_with_start_date),
            Organizations(**organization_args),
            ProjectCards(project_columns_stream, **repository_args_with_start_date),
            project_columns_stream,
            projects_stream,
            PullRequestCommentReactions(**repository_args_with_start_date),
            PullRequestCommits(parent=pull_requests_stream, **repository_args),
            PullRequestStats(**repository_args_with_start_date),
            ProjectsV2(**repository_args_with_start_date),
            pull_requests_stream,
            Releases(**repository_args_with_start_date),
            ReviewComments(**repository_args_with_start_date),
            Reviews(**repository_args_with_start_date),
            Stargazers(**repository_args_with_start_date),
            Tags(**repository_args),
            teams_stream,
            team_members_stream,
            Users(**organization_args),
            Workflows(**repository_args_with_start_date),
            workflow_runs_stream,
            WorkflowJobs(parent=workflow_runs_stream, **repository_args_with_start_date),
            TeamMemberships(parent=team_members_stream, **repository_args),
        ]

        return python_streams
