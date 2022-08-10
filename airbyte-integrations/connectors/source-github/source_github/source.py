#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import re
from typing import Any, Dict, List, Mapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import MultipleTokenAuthenticator

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
    WorkflowRuns,
    Workflows,
)

TOKEN_SEPARATOR = ","
DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM = 10
# To scan all the repos within orgnaization, organization name could be
# specified by using asteriks i.e. "airbytehq/*"
ORGANIZATION_PATTERN = re.compile("^.*/\\*$")


class SourceGithub(AbstractSource):
    @staticmethod
    def _generate_repositories(config: Mapping[str, Any], authenticator: MultipleTokenAuthenticator) -> Tuple[List[str], List[str]]:
        """
        Parse repositories config line and produce two lists of repositories.
        Args:
            config (dict): Dict representing connector's config
            authenticator(MultipleTokenAuthenticator): authenticator object
        Returns:
            Tuple[List[str], List[str]]: Tuple of two lists: first representing
            repositories directly mentioned in config and second is
            organization repositories from orgs/{org}/repos request.
        """
        repositories = list(filter(None, config["repository"].split(" ")))

        if not repositories:
            raise Exception("Field `repository` required to be provided for connect to Github API")

        repositories_list: set = {repo for repo in repositories if not ORGANIZATION_PATTERN.match(repo)}
        organizations = [org.split("/")[0] for org in repositories if org not in repositories_list]
        organisation_repos = set()
        if organizations:
            repos = Repositories(authenticator=authenticator, organizations=organizations)
            for stream in repos.stream_slices(sync_mode=SyncMode.full_refresh):
                organisation_repos = organisation_repos.union(
                    {r["full_name"] for r in repos.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream)}
                )

        return list(repositories_list), list(organisation_repos)

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
            # In case of getting repository list for given organization was
            # successfull no need of checking stats for every repository within
            # that organization.
            # Since we have "repo" scope requested it should grant access to private repos as well:
            # https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes
            repositories, _ = self._generate_repositories(config=config, authenticator=authenticator)

            repository_stats_stream = RepositoryStats(
                authenticator=authenticator,
                repositories=repositories,
                page_size_for_large_streams=config.get("page_size_for_large_streams", DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM),
            )
            for stream_slice in repository_stats_stream.stream_slices(sync_mode=SyncMode.full_refresh):
                next(repository_stats_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice), None)
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
        repos, organization_repos = self._generate_repositories(config=config, authenticator=authenticator)
        repositories = repos + organization_repos

        organizations = list({org.split("/")[0] for org in repositories})
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
            WorkflowRuns(**repository_args_with_start_date),
            TeamMemberships(parent=team_members_stream, **repository_args),
        ]
