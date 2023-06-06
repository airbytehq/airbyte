#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, List, Mapping, Set, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import MultipleTokenAuthenticator
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
    Deployments,
    Events,
    IssueCommentReactions,
    IssueEvents,
    IssueLabels,
    IssueMilestones,
    IssueReactions,
    Issues,
    Organizations,
    ProjectCards,
    ProjectColumns,
    Projects,
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


class SourceGithub(AbstractSource):
    @staticmethod
    def _get_and_prepare_repositories_config(config: Mapping[str, Any]) -> Set[str]:
        """
        _get_and_prepare_repositories_config gets set of repositories names from config and removes simple errors that user could provide
        Args:
            config: Dict representing connector's config
        Returns:
            set of provided repositories
        """
        config_repositories = set(filter(None, config["repository"].split(" ")))
        return config_repositories

    @staticmethod
    def _get_org_repositories(config: Mapping[str, Any], authenticator: MultipleTokenAuthenticator) -> Tuple[List[str], List[str]]:
        """
        Parse config.repository and produce two lists: organizations, repositories.
        Args:
            config (dict): Dict representing connector's config
            authenticator(MultipleTokenAuthenticator): authenticator object
        """
        config_repositories = SourceGithub._get_and_prepare_repositories_config(config)

        repositories = set()
        organizations = set()
        unchecked_repos = set()
        unchecked_orgs = set()

        for org_repos in config_repositories:
            org, _, repos = org_repos.partition("/")
            if repos == "*":
                unchecked_orgs.add(org)
            else:
                unchecked_repos.add(org_repos)

        if unchecked_orgs:
            stream = Repositories(authenticator=authenticator, organizations=unchecked_orgs)
            for record in read_full_refresh(stream):
                repositories.add(record["full_name"])
                organizations.add(record["organization"])

        unchecked_repos = unchecked_repos - repositories
        if unchecked_repos:
            stream = RepositoryStats(
                authenticator=authenticator,
                repositories=unchecked_repos,
                # This parameter is deprecated and in future will be used sane default, page_size: 10
                page_size_for_large_streams=config.get("page_size_for_large_streams", constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM),
            )
            for record in read_full_refresh(stream):
                repositories.add(record["full_name"])
                organization = record.get("organization", {}).get("login")
                if organization:
                    organizations.add(organization)

        return list(organizations), list(repositories)

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
        requests_per_hour = config.get("requests_per_hour")
        if requests_per_hour:
            return MultipleTokenAuthenticatorWithRateLimiter(
                tokens=tokens,
                auth_method="token",
                requests_per_hour=requests_per_hour,
            )
        return MultipleTokenAuthenticator(tokens=tokens, auth_method="token")

    @staticmethod
    def _get_branches_data(selected_branches: str, full_refresh_args: Dict[str, Any] = None) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
        selected_branches = set(filter(None, selected_branches.split(" ")))

        # Get the default branch for each repository
        default_branches = {}
        repository_stats_stream = RepositoryStats(**full_refresh_args)
        for stream_slice in repository_stats_stream.stream_slices(sync_mode=SyncMode.full_refresh):
            default_branches.update(
                {
                    repo_stats["full_name"]: repo_stats["default_branch"]
                    for repo_stats in repository_stats_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
                }
            )

        all_branches = []
        branches_stream = Branches(**full_refresh_args)
        for stream_slice in branches_stream.stream_slices(sync_mode=SyncMode.full_refresh):
            for branch in branches_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                all_branches.append(f"{branch['repository']}/{branch['name']}")

        # Create mapping of repository to list of branches to pull commits for
        # If no branches are specified for a repo, use its default branch
        branches_to_pull: Dict[str, List[str]] = {}
        for repo in full_refresh_args["repositories"]:
            repo_branches = []
            for branch in selected_branches:
                branch_parts = branch.split("/", 2)
                if "/".join(branch_parts[:2]) == repo and branch in all_branches:
                    repo_branches.append(branch_parts[-1])
            if not repo_branches:
                repo_branches = [default_branches[repo]]

            branches_to_pull[repo] = repo_branches

        return default_branches, branches_to_pull

    def user_friendly_error_message(self, message: str) -> str:
        user_message = ""
        if "404 Client Error: Not Found for url: https://api.github.com/repos/" in message:
            # 404 Client Error: Not Found for url: https://api.github.com/repos/airbytehq/airbyte3?per_page=100
            full_repo_name = message.split("https://api.github.com/repos/")[1].split("?")[0]
            user_message = f'Repo name: "{full_repo_name}" is unknown, "repository" config option should use existing full repo name <organization>/<repository>'
        elif "404 Client Error: Not Found for url: https://api.github.com/orgs/" in message:
            # 404 Client Error: Not Found for url: https://api.github.com/orgs/airbytehqBLA/repos?per_page=100
            org_name = message.split("https://api.github.com/orgs/")[1].split("/")[0]
            user_message = f'Organization name: "{org_name}" is unknown, "repository" config option should be updated'
        elif "401 Client Error: Unauthorized for url" in message:
            # 401 Client Error: Unauthorized for url: https://api.github.com/orgs/datarootsio/repos?per_page=100&sort=updated&direction=desc
            user_message = "Bad credentials, re-authentication or access token renewal is required"
        return user_message

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            authenticator = self._get_authenticator(config)
            _, repositories = self._get_org_repositories(config=config, authenticator=authenticator)
            if not repositories:
                return False, "Invalid repositories. Valid examples: airbytehq/airbyte airbytehq/another-repo airbytehq/* airbytehq/airbyte"
            return True, None

        except Exception as e:
            message = repr(e)
            user_message = self.user_friendly_error_message(message)
            return False, user_message or message

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self._get_authenticator(config)
        try:
            organizations, repositories = self._get_org_repositories(config=config, authenticator=authenticator)
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
            )
            raise AirbyteTracedException(
                internal_message="No streams available. Please check permissions",
                message=user_message,
                failure_type=FailureType.config_error,
            )

        # This parameter is deprecated and in future will be used sane default, page_size: 10
        page_size = config.get("page_size_for_large_streams", constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM)
        access_token_type, _ = self.get_access_token(config)

        organization_args = {"authenticator": authenticator, "organizations": organizations, "access_token_type": access_token_type}
        organization_args_with_start_date = {**organization_args, "start_date": config["start_date"]}

        repository_args = {
            "authenticator": authenticator,
            "repositories": repositories,
            "page_size_for_large_streams": page_size,
            "access_token_type": access_token_type,
        }
        repository_args_with_start_date = {**repository_args, "start_date": config["start_date"]}

        default_branches, branches_to_pull = self._get_branches_data(config.get("branch", ""), repository_args)
        pull_requests_stream = PullRequests(**repository_args_with_start_date)
        projects_stream = Projects(**repository_args_with_start_date)
        project_columns_stream = ProjectColumns(projects_stream, **repository_args_with_start_date)
        teams_stream = Teams(**organization_args)
        team_members_stream = TeamMembers(parent=teams_stream, **repository_args)
        workflow_runs_stream = WorkflowRuns(**repository_args_with_start_date)

        return [
            Assignees(**repository_args),
            Branches(**repository_args),
            Collaborators(**repository_args),
            Comments(**repository_args_with_start_date),
            CommitCommentReactions(**repository_args_with_start_date),
            CommitComments(**repository_args_with_start_date),
            Commits(**repository_args_with_start_date, branches_to_pull=branches_to_pull, default_branches=default_branches),
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
            pull_requests_stream,
            Releases(**repository_args_with_start_date),
            Repositories(**organization_args_with_start_date),
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
