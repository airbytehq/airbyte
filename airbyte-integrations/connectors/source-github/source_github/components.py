#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import re
from dataclasses import InitVar, dataclass, field
from typing import Any, List, Mapping, MutableMapping, Optional, Set, Tuple

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.transformations.config_transformations.config_transformation import ConfigTransformation
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

logger = logging.getLogger("airbyte")


@dataclass
class RepositoryListResolver(ConfigTransformation):
    """Resolves repository wildcard patterns and validates explicit repos at config time.

    Parses `config["repositories"]` entries:
    - Wildcard patterns like `org/*` or `org/prefix*` are expanded by calling
      `GET /orgs/{org}/repos` and filtering by regex.
    - Explicit repos like `org/repo` are validated by calling `GET /repos/{org}/repo`.

    After resolution, the following keys are injected into the config:
    - `_resolved_repositories`: deduplicated list of full repo names
    - `_resolved_organizations`: deduplicated list of organization names
    - `_repository_pattern`: compiled regex pattern string (or empty if no wildcards)
    """

    parameters: InitVar[Mapping[str, Any]]

    _api_url: str = field(default="https://api.github.com", init=False)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        pass

    def transform(self, config: MutableMapping[str, Any]) -> None:
        api_url = config.get("api_url", "https://api.github.com").rstrip("/")
        self._api_url = api_url

        tokens = self._extract_tokens(config)
        if not tokens:
            raise AirbyteTracedException(
                message="No authentication tokens found in config.",
                failure_type=FailureType.config_error,
            )

        config_repositories = set(config.get("repositories") or [])
        if not config_repositories:
            # Handle legacy "repository" field (space-delimited)
            legacy = config.get("repository", "")
            config_repositories = set(filter(None, legacy.split(" ")))

        organizations, repositories, pattern = self._resolve_repositories(
            config_repositories, tokens
        )

        config["_resolved_repositories"] = sorted(repositories)
        config["_resolved_organizations"] = sorted(organizations)
        config["_repository_pattern"] = pattern or ""

    @staticmethod
    def _extract_tokens(config: Mapping[str, Any]) -> List[str]:
        """Extract authentication tokens from config, handling multiple config shapes."""
        token_separator = ","

        if "access_token" in config:
            raw = config["access_token"]
        else:
            credentials = config.get("credentials", {})
            raw = credentials.get("access_token") or credentials.get("personal_access_token", "")

        if not raw:
            return []
        return [t.strip() for t in raw.split(token_separator) if t.strip()]

    def _resolve_repositories(
        self,
        config_repositories: Set[str],
        tokens: List[str],
    ) -> Tuple[List[str], List[str], Optional[str]]:
        """Resolve wildcard patterns and validate explicit repos.

        Returns (organizations, repositories, pattern).
        """
        repositories: Set[str] = set()
        organizations: Set[str] = set()
        unchecked_repos: Set[str] = set()
        unchecked_orgs: Set[str] = set()
        pattern: Optional[str] = None

        for org_repos in config_repositories:
            _, _, repos = org_repos.partition("/")
            if "*" in repos:
                unchecked_orgs.add(org_repos)
            else:
                unchecked_repos.add(org_repos)

        token_index = 0

        if unchecked_orgs:
            org_names = [org.split("/")[0] for org in unchecked_orgs]
            pattern = "|".join(
                [f"({org.replace('*', '.*')})" for org in unchecked_orgs]
            )
            compiled_pattern = re.compile(pattern)

            for org_name in org_names:
                org_repos = self._fetch_org_repos(
                    org_name, tokens[token_index % len(tokens)]
                )
                for repo in org_repos:
                    full_name = repo.get("full_name", "")
                    if compiled_pattern.match(full_name):
                        repositories.add(full_name)
                        org = repo.get("owner", {}).get("login", org_name)
                        organizations.add(org)

        unchecked_repos = unchecked_repos - repositories
        if unchecked_repos:
            for repo_name in unchecked_repos:
                repo_data = self._validate_repo(
                    repo_name, tokens[token_index % len(tokens)]
                )
                if repo_data:
                    repositories.add(repo_data["full_name"])
                    org_login = (repo_data.get("organization") or {}).get("login")
                    if org_login:
                        organizations.add(org_login)

        return sorted(organizations), sorted(repositories), pattern

    def _fetch_org_repos(self, org_name: str, token: str) -> List[Mapping[str, Any]]:
        """Fetch all repositories for an organization, handling pagination."""
        all_repos: List[Mapping[str, Any]] = []
        url = f"{self._api_url}/orgs/{org_name}/repos"
        params = {"per_page": "100", "sort": "updated", "direction": "desc"}
        headers = self._build_headers(token)

        while url:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            if response.status_code == 404:
                logger.warning(
                    "Organization '%s' not found (HTTP 404). Skipping.", org_name
                )
                break
            if response.status_code == 403:
                logger.warning(
                    "Access denied for organization '%s' (HTTP 403). Skipping.",
                    org_name,
                )
                break
            response.raise_for_status()
            all_repos.extend(response.json())

            # Follow pagination via Link header
            next_link = response.links.get("next", {}).get("url")
            url = next_link
            params = {}  # URL already contains params for next page

        return all_repos

    def _validate_repo(
        self, repo_name: str, token: str
    ) -> Optional[Mapping[str, Any]]:
        """Validate a single explicit repository by calling GET /repos/{owner}/{repo}."""
        url = f"{self._api_url}/repos/{repo_name}"
        headers = self._build_headers(token)

        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 404:
            logger.warning(
                "Repository '%s' not found (HTTP 404). Skipping.", repo_name
            )
            return None
        if response.status_code == 403:
            logger.warning(
                "Access denied for repository '%s' (HTTP 403). Skipping.", repo_name
            )
            return None
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _build_headers(token: str) -> Mapping[str, str]:
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "PostmanRuntime/7.28.0",
        }
