#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import re
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, MutableMapping, Optional, Set, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.auth.rate_limited_multiple_token import (
    RateLimitedMultipleTokenAuthenticator,
    TokenQuota,
)
from airbyte_cdk.sources.declarative.transformations.config_transformations.config_transformation import ConfigTransformation
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


logger = logging.getLogger("airbyte")


# TODO(https://github.com/airbytehq/airbyte-internal-issues/issues/16512): remove once the
# remaining Python streams migrate to the manifest. The manifest resolver streams
# (`repositories_resolver`/`repository_stats`) are the canonical resolution path; this class
# mirrors their semantics for the Python streams during the transition.
@dataclass
class RepositoryListResolver(ConfigTransformation):
    """Resolves repository wildcard patterns and validates explicit repos at config time.

    Parses `config["repositories"]` entries:
    - Wildcard patterns like `org/*` or `org/prefix*` are expanded by calling
      `GET /orgs/{org}/repos` and filtering by regex.
    - Explicit repos like `org/repo` are validated by calling `GET /repos/{org}/{repo}`;
      entries that 404 are skipped with a warning.

    Requests are signed by the same `RateLimitedMultipleTokenAuthenticator` the manifest
    uses (token rotation + quota-aware waits) and retried with backoff on transient errors.

    After resolution, the following keys are injected into the config:
    - `_resolved_repositories`: deduplicated list of full repo names
    - `_resolved_organizations`: deduplicated list of organization names (only orgs that
      actually exist; user-owned repos contribute a repository but no organization)
    """

    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._api_url = "https://api.github.com"
        self._session: Optional[requests.Session] = None

    def transform(self, config: MutableMapping[str, Any]) -> None:
        self._api_url = config.get("api_url", "https://api.github.com").rstrip("/")

        tokens = self._extract_tokens(config)
        if not tokens:
            raise AirbyteTracedException(
                message="No authentication tokens found in config.",
                failure_type=FailureType.config_error,
            )
        self._session = self._build_session(tokens)

        config_repositories = set(config.get("repositories") or [])
        if not config_repositories:
            # Handle legacy "repository" field (space-delimited)
            legacy = config.get("repository", "")
            config_repositories = set(filter(None, legacy.split(" ")))

        organizations, repositories = self._resolve_repositories(config_repositories)

        config["_resolved_repositories"] = sorted(repositories)
        config["_resolved_organizations"] = sorted(organizations)

    def _build_session(self, tokens: List[str]) -> requests.Session:
        session = requests.Session()
        session.auth = RateLimitedMultipleTokenAuthenticator(
            tokens=tokens,
            quotas=[
                TokenQuota(
                    name="rest",
                    remaining_path=["resources", "core", "remaining"],
                    reset_path=["resources", "core", "reset"],
                    limit_path=["resources", "core", "limit"],
                )
            ],
            quota_status_url=f"{self._api_url}/rate_limit",
            quota_status_headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            auth_method="token",
        )
        retry = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            respect_retry_after_header=True,
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "PostmanRuntime/7.28.0",
            }
        )
        return session

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

    def _resolve_repositories(self, config_repositories: Set[str]) -> Tuple[List[str], List[str]]:
        """Resolve wildcard patterns and validate explicit repos.

        Returns (organizations, repositories).
        """
        repositories: Set[str] = set()
        organizations: Set[str] = set()
        unchecked_repos: Set[str] = set()
        unchecked_orgs: Set[str] = set()

        for org_repos in config_repositories:
            _, _, repos = org_repos.partition("/")
            if "*" in repos:
                unchecked_orgs.add(org_repos)
            else:
                unchecked_repos.add(org_repos)

        if unchecked_orgs:
            org_names = [org.split("/")[0] for org in unchecked_orgs]
            pattern = "|".join([f"({org.replace('*', '.*')})" for org in unchecked_orgs])
            compiled_pattern = re.compile(pattern)

            for org_name in org_names:
                org_repos = self._fetch_org_repos(org_name)
                for repo in org_repos:
                    full_name = repo.get("full_name", "")
                    if compiled_pattern.match(full_name):
                        repositories.add(full_name)
                        org = repo.get("owner", {}).get("login", org_name)
                        organizations.add(org)

        unchecked_repos = unchecked_repos - repositories
        for repo_name in unchecked_repos:
            repo = self._fetch_repo(repo_name)
            if repo is None:
                continue
            repositories.add(repo.get("full_name") or repo_name)
            organization = (repo.get("organization") or {}).get("login")
            if organization:
                organizations.add(organization)

        return sorted(organizations), sorted(repositories)

    def _fetch_org_repos(self, org_name: str) -> List[Mapping[str, Any]]:
        """Fetch all repositories for an organization, handling pagination."""
        assert self._session is not None
        all_repos: List[Mapping[str, Any]] = []
        url: Optional[str] = f"{self._api_url}/orgs/{org_name}/repos"
        params: Mapping[str, str] = {"per_page": "100", "sort": "updated", "direction": "desc"}

        while url:
            response = self._session.get(url, params=params, timeout=30)
            if response.status_code == 404:
                logger.warning("Organization '%s' not found (HTTP 404). Skipping.", org_name)
                break
            if response.status_code == 403:
                logger.warning("Access denied for organization '%s' (HTTP 403). Skipping.", org_name)
                break
            response.raise_for_status()
            all_repos.extend(response.json())

            # Follow pagination via Link header
            url = response.links.get("next", {}).get("url")
            params = {}  # URL already contains params for next page

        return all_repos

    def _fetch_repo(self, repo_name: str) -> Optional[Mapping[str, Any]]:
        """Validate an explicit `org/repo` entry and return its metadata, or `None` if unavailable."""
        assert self._session is not None
        response = self._session.get(f"{self._api_url}/repos/{repo_name}", params={"per_page": "100"}, timeout=30)
        if response.status_code == 404:
            logger.warning("Repository '%s' not found (HTTP 404). Skipping.", repo_name)
            return None
        if response.status_code == 403:
            logger.warning("Access denied for repository '%s' (HTTP 403). Skipping.", repo_name)
            return None
        response.raise_for_status()
        return response.json()
