#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import fnmatch
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
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import MultipleTokenAuthenticator
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_github.utils import MultipleTokenAuthenticatorWithRateLimiter

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
    Repositories,
    RepositoryStats,
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
from .utils import read_full_refresh


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

        The concurrent streams come from `super().streams()` (the manifest), which is
        empty today and does no network work. The synchronous streams are resolved by
        `AbstractSource.read()` itself, so `SourceGithub.streams()` (which performs live
        org/repo resolution) is only invoked once per sync. As streams are migrated from
        Python to the manifest, they automatically move from the synchronous to the
        concurrent path.
        """
        concurrent_streams = super().streams(config=self._config or config)
        concurrent_stream_names = {stream.name for stream in concurrent_streams}

        concurrent_catalog = ConfiguredAirbyteCatalog(streams=[s for s in catalog.streams if s.stream.name in concurrent_stream_names])
        if concurrent_catalog.streams:
            selected = self._select_streams(streams=concurrent_streams, configured_catalog=concurrent_catalog)
            if selected:
                yield from self._concurrent_source.read(selected)

        synchronous_catalog = ConfiguredAirbyteCatalog(streams=[s for s in catalog.streams if s.stream.name not in concurrent_stream_names])
        if synchronous_catalog.streams:
            yield from AbstractSource.read(self, logger, config, synchronous_catalog, state)

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

    @staticmethod
    def _get_org_repositories(
        config: Mapping[str, Any], authenticator: MultipleTokenAuthenticator, is_check_connection: bool = False
    ) -> Tuple[List[str], List[str], Optional[str]]:
        """
        Parse config/repositories and produce two lists: organizations, repositories.
        Args:
            config (dict): Dict representing connector's config
            authenticator(MultipleTokenAuthenticator): authenticator object
        """
        configured_repository_selectors = set(config.get("repositories"))
        included_repository_selectors = {repository for repository in configured_repository_selectors if not repository.startswith("!")}
        excluded_repository_selectors = {
            repository.removeprefix("!") for repository in configured_repository_selectors if repository.startswith("!")
        }

        repositories = set()
        organizations = set()
        unchecked_repos = set()
        unchecked_orgs = set()

        for org_repos in included_repository_selectors:
            if any(fnmatch.fnmatchcase(org_repos, excluded_repository) for excluded_repository in excluded_repository_selectors):
                continue
            _, _, repos = org_repos.partition("/")
            if "*" in repos:
                unchecked_orgs.add(org_repos)
            else:
                unchecked_repos.add(org_repos)

        included_repository_pattern = "|".join(fnmatch.translate(repository) for repository in unchecked_orgs)
        excluded_repository_pattern = "|".join(fnmatch.translate(repository) for repository in excluded_repository_selectors)
        pattern = included_repository_pattern or None
        if excluded_repository_pattern:
            pattern = f"(?!{excluded_repository_pattern})(?:{included_repository_pattern or '.*'})"

        if unchecked_orgs:
            org_names = [org.split("/")[0] for org in unchecked_orgs]
            stream = Repositories(authenticator=authenticator, organizations=org_names, api_url=config.get("api_url"), pattern=pattern)
            stream.exit_on_rate_limit = True if is_check_connection else False
            for record in read_full_refresh(stream):
                repositories.add(record["full_name"])
                organizations.add(record["organization"])

        unchecked_repos = unchecked_repos - repositories
        if unchecked_repos:
            stream = RepositoryStats(
                authenticator=authenticator,
                repositories=list(unchecked_repos),
                api_url=config.get("api_url"),
                # This parameter is deprecated and in future will be used sane default, page_size: 10
                page_size_for_large_streams=config.get("page_size_for_large_streams", constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM),
            )
            stream.exit_on_rate_limit = True if is_check_connection else False
            for record in read_full_refresh(stream):
                repositories.add(record["full_name"])
                organization = record.get("organization", {}).get("login")
                if organization:
                    organizations.add(organization)

        return list(organizations), list(repositories), pattern

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

    def _get_authenticator(self, config: Mapping[str, Any]):
        _, token = self.get_access_token(config)
        tokens = [t.strip() for t in token.split(constants.TOKEN_SEPARATOR)]
        return MultipleTokenAuthenticatorWithRateLimiter(tokens=tokens)

    def _validate_and_transform_config(self, config: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        config = self._ensure_default_values(config)
        config = self._validate_repositories(config)
        config = self._validate_branches(config)
        return config

    def _ensure_default_values(self, config: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        config.setdefault("api_url", "https://api.github.com")
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
        user_message = ""
        if "404 Client Error: Not Found for url: https://api.github.com/repos/" in message:
            # 404 Client Error: Not Found for url: https://api.github.com/repos/airbytehq/airbyte3?per_page=100
            full_repo_name = message.split("https://api.github.com/repos/")[1].split("?")[0]
            user_message = f'Repo name: "{full_repo_name}" is unknown, "repository" config option should use existing full repo name <organization>/<repository>'
        elif "404 Client Error: Not Found for url: https://api.github.com/orgs/" in message:
            # 404 Client Error: Not Found for url: https://api.github.com/orgs/airbytehqBLA/repos?per_page=100
            org_name = message.split("https://api.github.com/orgs/")[1].split("/")[0]
            user_message = f'Organization name: "{org_name}" is unknown, "repository" config option should be updated. Please validate your repository config.'
        elif "401 Client Error: Unauthorized for url" in message or ("Error: Unauthorized" in message and "401" in message):
            user_message = (
                "GitHub authentication failed (HTTP 401). Please verify your Personal Access Token or OAuth credentials "
                "are valid and not expired."
            )
        return user_message

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        config = self._validate_and_transform_config(config)
        try:
            authenticator = self._get_authenticator(config)
            _, repositories, _ = self._get_org_repositories(config=config, authenticator=authenticator, is_check_connection=True)
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
        authenticator = self._get_authenticator(config)
        config = self._validate_and_transform_config(config)
        try:
            organizations, repositories, pattern = self._get_org_repositories(config=config, authenticator=authenticator)
        except Exception as e:
            message = repr(e)
            user_message = self.user_friendly_error_message(message)
            if user_message:
                raise AirbyteTracedException(
                    internal_message=message, message=user_message, failure_type=FailureType.config_error, exception=e
                )
            else:
                raise e

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
        max_waiting_time = config.get("max_waiting_time", 120) * 60
        organization_args = {
            "authenticator": authenticator,
            "organizations": organizations,
            "api_url": config.get("api_url"),
            "access_token_type": access_token_type,
            "max_waiting_time": max_waiting_time,
        }
        start_date = config.get("start_date")
        organization_args_with_start_date = {**organization_args, "start_date": start_date}

        repository_args = {
            "authenticator": authenticator,
            "api_url": config.get("api_url"),
            "repositories": repositories,
            "page_size_for_large_streams": page_size,
            "access_token_type": access_token_type,
            "max_waiting_time": max_waiting_time,
        }
        repository_args_with_start_date = {**repository_args, "start_date": start_date}

        pull_requests_stream = PullRequests(**repository_args_with_start_date)
        projects_stream = Projects(**repository_args_with_start_date)
        project_columns_stream = ProjectColumns(projects_stream, **repository_args_with_start_date)
        teams_stream = Teams(**organization_args)
        team_members_stream = TeamMembers(parent=teams_stream, **repository_args)
        workflow_runs_stream = WorkflowRuns(**repository_args_with_start_date)

        return [
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
            Repositories(**organization_args_with_start_date, pattern=pattern),
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
