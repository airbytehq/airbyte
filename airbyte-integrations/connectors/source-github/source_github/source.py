#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
    Events,
    IssueCommentReactions,
    IssueEvents,
    IssueLabels,
    IssueMilestones,
    IssueReactions,
    Issues,
    Organizations,
    Projects,
    PullRequestCommentReactions,
    PullRequests,
    PullRequestStats,
    Releases,
    Repositories,
    RepositoryStats,
    ReviewComments,
    Reviews,
    Stargazers,
    Tags,
    Teams,
    Users,
)

TOKEN_SEPARATOR = ","
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
            )
            for stream_slice in repository_stats_stream.stream_slices(sync_mode=SyncMode.full_refresh):
                next(repository_stats_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice), None)
            return True, None
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self._get_authenticator(config)
        repos, organization_repos = self._generate_repositories(config=config, authenticator=authenticator)
        repositories = repos + organization_repos

        organizations = list({org.split("/")[0] for org in repositories})
        full_refresh_args = {"authenticator": authenticator, "repositories": repositories}
        incremental_args = {**full_refresh_args, "start_date": config["start_date"]}
        organization_args = {"authenticator": authenticator, "organizations": organizations}
        default_branches, branches_to_pull = self._get_branches_data(config.get("branch", ""), full_refresh_args)

        return [
            Assignees(**full_refresh_args),
            Branches(**full_refresh_args),
            Collaborators(**full_refresh_args),
            Comments(**incremental_args),
            CommitCommentReactions(**incremental_args),
            CommitComments(**incremental_args),
            Commits(**incremental_args, branches_to_pull=branches_to_pull, default_branches=default_branches),
            Events(**incremental_args),
            IssueCommentReactions(**incremental_args),
            IssueEvents(**incremental_args),
            IssueLabels(**full_refresh_args),
            IssueMilestones(**incremental_args),
            IssueReactions(**incremental_args),
            Issues(**incremental_args),
            Organizations(**organization_args),
            Projects(**incremental_args),
            PullRequestCommentReactions(**incremental_args),
            PullRequestStats(**full_refresh_args),
            PullRequests(**incremental_args),
            Releases(**incremental_args),
            Repositories(**organization_args),
            ReviewComments(**incremental_args),
            Reviews(**full_refresh_args),
            Stargazers(**incremental_args),
            Tags(**full_refresh_args),
            Teams(**organization_args),
            Users(**organization_args),
        ]
