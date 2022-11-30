#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, List, Mapping, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.declarative.checks.connection_checker import HTTPAvailabilityStrategy
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import MultipleTokenAuthenticator
from requests.exceptions import HTTPError

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

TOKEN_SEPARATOR = ","
DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM = 10


class GithubAvailabilityStrategy(HTTPAvailabilityStrategy):
    def check_availability(self, stream: Stream) -> Tuple[bool, any]:
        stream_slice = self._get_stream_slice(stream)
        # get out the stream_slice parts for later use.
        organisation = stream_slice.get("organization", "")
        repository = stream_slice.get("repository", "")
        try:
            records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
            next(records)
            return True, None
        except HTTPError as e:
            if e.response.status_code == requests.codes.NOT_FOUND:
                # A lot of streams are not available for repositories owned by a user instead of an organization.
                if isinstance(stream, Organizations):
                    error_msg = (
                        f"`{stream.__class__.__name__}` stream isn't available for organization `{stream_slice['organization']}`."
                    )
                else:
                    error_msg = (
                        f"`{stream.__class__.__name__}` stream isn't available for repository `{stream_slice['repository']}`."
                    
            elif e.response.status_code == requests.codes.FORBIDDEN:
                error_msg = str(e.response.json().get("message"))
                # When using the `check_availability` method, we should raise an error if we do not have access to the repository.
                if isinstance(stream, Repositories):
                    raise e
                # When `403` for the stream, that has no access to the organization's teams, based on OAuth Apps Restrictions:
                # https://docs.github.com/en/organizations/restricting-access-to-your-organizations-data/enabling-oauth-app-access-restrictions-for-your-organization
                # For all `Organization` based streams
                elif isinstance(stream, Organizations) or isinstance(stream, Teams) or isinstance(stream, Users):
                    error_msg = (
                        f"`{stream.name}` stream isn't available for organization `{organisation}`. Full error message: {error_msg}"
                    )
                # For all other `Repository` base streams
                else:
                    error_msg = (
                        f"`{stream.name}` stream isn't available for repository `{repository}`. Full error message: {error_msg}"
                    )
            elif e.response.status_code == requests.codes.GONE and isinstance(stream, Projects):
                # Some repos don't have projects enabled and we we get "410 Client Error: Gone for
                # url: https://api.github.com/repos/xyz/projects?per_page=100" error.
                error_msg = f"`Projects` stream isn't available for repository `{stream_slice['repository']}`."
            elif e.response.status_code == requests.codes.CONFLICT:
                error_msg = (
                    f"`{stream.name}` stream isn't available for repository "
                    f"`{stream_slice['repository']}`, it seems like this repository is empty."
                )
            elif e.response.status_code == requests.codes.SERVER_ERROR and isinstance(stream, WorkflowRuns):
                error_msg = f"Syncing `{stream.name}` stream isn't available for repository `{stream_slice['repository']}`."

            return False, error_msg


class SourceGithub(AbstractSource):
    @property
    def availability_strategy(self):
        return GithubAvailabilityStrategy()

    @staticmethod
    def _get_org_repositories(config: Mapping[str, Any], authenticator: MultipleTokenAuthenticator) -> Tuple[List[str], List[str]]:
        """
        Parse config.repository and produce two lists: organizations, repositories.
        Args:
            config (dict): Dict representing connector's config
            authenticator(MultipleTokenAuthenticator): authenticator object
        """
        config_repositories = set(filter(None, config["repository"].split(" ")))
        if not config_repositories:
            raise Exception("Field `repository` required to be provided for connect to Github API")

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
                page_size_for_large_streams=config.get("page_size_for_large_streams", DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM),
            )
            for record in read_full_refresh(stream):
                repositories.add(record["full_name"])
                organization = record.get("organization", {}).get("login")
                if organization:
                    organizations.add(organization)

        return list(organizations), list(repositories)

    @staticmethod
    def _get_authenticator(config: Dict[str, Any]):
        # Before we supported oauth, personal_access_token was called `access_token` and it lived at the
        # config root. So we first check to make sure any backwards compatbility is handled.
        token = config.get("access_token")
        if not token:
            creds = config.get("credentials")
            token = creds.get("access_token") or creds.get("personal_access_token")
        tokens = [t.strip() for t in token.split(TOKEN_SEPARATOR)]
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

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            authenticator = self._get_authenticator(config)
            _, repositories = self._get_org_repositories(config=config, authenticator=authenticator)
            if not repositories:
                return False, "no valid repositories found"
            return True, None

        except Exception as e:
            message = repr(e)
            if "404 Client Error: Not Found for url: https://api.github.com/repos/" in message:
                # HTTPError('404 Client Error: Not Found for url: https://api.github.com/repos/airbytehq/airbyte3?per_page=100')"
                full_repo_name = message.split("https://api.github.com/repos/")[1]
                full_repo_name = full_repo_name.split("?")[0]
                message = f'Unknown repo name: "{full_repo_name}", use existing full repo name <organization>/<repository>'
            elif "404 Client Error: Not Found for url: https://api.github.com/orgs/" in message:
                # HTTPError('404 Client Error: Not Found for url: https://api.github.com/orgs/airbytehqBLA/repos?per_page=100')"
                org_name = message.split("https://api.github.com/orgs/")[1]
                org_name = org_name.split("/")[0]
                message = f'Unknown organization name: "{org_name}"'

            return False, message

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self._get_authenticator(config)
        organizations, repositories = self._get_org_repositories(config=config, authenticator=authenticator)
        page_size = config.get("page_size_for_large_streams", DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM)

        organization_args = {"authenticator": authenticator, "organizations": organizations}
        organization_args_with_start_date = {**organization_args, "start_date": config["start_date"]}
        repository_args = {"authenticator": authenticator, "repositories": repositories, "page_size_for_large_streams": page_size}
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
