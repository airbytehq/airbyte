import time
import jwt
import requests
import yaml
import os
from typing import Any, Mapping, Iterable, List, Optional

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream

logger = AirbyteLogger()


def create_jwt(app_id: int, private_key: str) -> str:
    """
    Create a short-lived JWT for GitHub App authentication.

    This JWT is used to obtain installation tokens that grant scoped access
    under a particular GitHub App installation.
    """
    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + 540,  # 9 minutes lifespan to meet GitHub requirements
        "iss": app_id
    }

    token = jwt.encode(payload, private_key, algorithm="RS256")
    logger.debug("Successfully created an app-level JWT.")
    return token


def paginate_github(url: str, headers: Mapping[str, Any]) -> List[Any]:
    """
    Paginate through GitHub API endpoints following 'next' links until all pages are fetched.

    Parameters:
        url (str): The initial URL to request.
        headers (Mapping[str, Any]): HTTP headers, including authorization.

    Returns:
        List[Any]: A combined list of all records retrieved from all pages.
    """
    logger.debug(f"Initiating pagination for: {url}")
    results = []
    while url:
        logger.debug(f"Requesting GitHub endpoint: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict):
            if "organizations" in data:
                # Enterprise org listing
                org_count = len(data["organizations"])
                logger.debug(f"Received {org_count} organizations from enterprise listing.")
                results.extend(data["organizations"])

            elif "workflow_runs" in data:
                # GitHub Actions workflow runs
                run_count = len(data["workflow_runs"])
                logger.debug(f"Received {run_count} workflow runs from endpoint.")
                results.extend(data["workflow_runs"])

            elif isinstance(data.get("items"), list):
                # Some search APIs return {"total_count": X, "items": [...]}
                # e.g., searching code, issues, repos, or users
                item_count = len(data["items"])
                logger.debug(f"Received {item_count} items from search endpoint.")
                results.extend(data["items"])

            elif isinstance(data.get("repositories"), list):
                # Some GitHub endpoints respond with "repositories": [...]
                repo_count = len(data["repositories"])
                logger.debug(f"Received {repo_count} repositories from endpoint.")
                results.extend(data["repositories"])

            else:
                # If you want to handle even more shapes, add more conditions
                logger.debug("Received an unexpected dictionary shape from GitHub endpoint.")

        elif isinstance(data, list):
            # A plain list of objects
            item_count = len(data)
            logger.debug(f"Received {item_count} items from endpoint.")
            results.extend(data)

        else:
            logger.debug("Received an unexpected data shape from GitHub endpoint.")

        # Check for pagination link
        url = None
        if "Link" in response.headers:
            links = response.headers["Link"].split(",")
            for link in links:
                if 'rel="next"' in link:
                    parts = link.split(";")
                    url = parts[0].strip("<> ")
                    logger.debug(f"Next page detected: {url}")

    logger.info(f"Pagination complete. Retrieved a total of {len(results)} records.")
    return results


class BaseGithubStream(Stream):
    """
    Base stream class providing common functionality for all GitHub streams:
    - Creating and using JWT for app-level auth.
    - Retrieving installation tokens for a specific org or enterprise.
    - Common logging and schema loading.

    Assumes that 'app_id' and 'private_key' represent a GitHub App, and that 'org_or_enterprise'
    is either an organization or enterprise slug depending on 'is_enterprise'.
    """

    primary_key = None

    def __init__(self, app_id: int, private_key: str, org_or_enterprise: str, is_enterprise: bool):
        super().__init__()
        self.app_id = app_id
        self.private_key = private_key
        self.org_or_enterprise = org_or_enterprise
        self.is_enterprise = is_enterprise
        self._installation_token: Optional[str] = None

    def get_app_jwt(self) -> str:
        logger.debug("Generating app-level JWT for GitHub App.")
        return create_jwt(self.app_id, self.private_key)

    def get_installations(self, jwt_token: str) -> List[dict]:
        """
        Fetch all installations for the app.

        Parameters:
            jwt_token (str): The app-level JWT for authentication.

        Returns:
            List[dict]: A list of installations with metadata.
        """
        logger.debug("Fetching installations for the GitHub App...")
        response = requests.get(
            "https://api.github.com/app/installations",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json"
            }
        )
        response.raise_for_status()
        installations = response.json()
        logger.debug(f"Found {len(installations)} installations for the app.")
        return installations

    def get_installation_token(self, installation_id: int) -> str:
        """
        Exchange the app-level JWT for an installation access token.

        Parameters:
            installation_id (int): The ID of the installation for which we want an access token.

        Returns:
            str: The installation access token.
        """
        logger.debug(f"Requesting installation token for installation ID: {installation_id}")
        jwt_token = self.get_app_jwt()
        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json"
            }
        )
        response.raise_for_status()
        token = response.json()["token"]
        logger.debug("Installation token acquired successfully.")
        return token

    def get_installation_token_for_target(self) -> str:
        """
        Retrieve and cache the installation token for the specified org or enterprise.

        Returns:
            str: The cached or newly obtained installation token.
        """
        if self._installation_token is None:
            logger.debug("No cached installation token found. Attempting to fetch a new one.")
            jwt_token = self.get_app_jwt()
            installations = self.get_installations(jwt_token)
            target_type = "Enterprise" if self.is_enterprise else "Organization"

            logger.debug(f"Looking for installation matching: {self.org_or_enterprise} ({target_type})")
            target_installations = [
                inst for inst in installations
                if inst["account"]["login"] == self.org_or_enterprise and inst["account"]["type"] == target_type
            ]

            if not target_installations:
                error_msg = f"No installation found for {self.org_or_enterprise} ({target_type})"
                logger.error(error_msg)
                raise Exception(error_msg)

            installation_id = target_installations[0]["id"]
            logger.info(f"Found installation {installation_id} for {self.org_or_enterprise} ({target_type}).")
            self._installation_token = self.get_installation_token(installation_id)
        else:
            logger.debug("Using cached installation token.")
        return self._installation_token

    def load_schema(self, name: str) -> dict:
        """
        Load a JSON schema from a YAML file located in the schemas directory.

        Parameters:
            name (str): The base name of the YAML file without extension.

        Returns:
            dict: The parsed schema dictionary.
        """
        schema_path = os.path.join(os.path.dirname(__file__), "schemas", f"{name}.json")
        logger.debug(f"Loading schema from {schema_path}")
        with open(schema_path, "r") as f:
            schema = yaml.safe_load(f)
        logger.debug(f"Schema for {name} loaded successfully.")
        return schema


class ParentOrgsStream(BaseGithubStream):
    """
    If 'is_enterprise' is True, this stream lists all organizations under the given enterprise.
    If False, it yields a single record representing the given org.
    This acts as a parent stream for other streams that need org information.
    """

    name = "enterprise_orgs"  # <-- class-level attribute

    def get_json_schema(self) -> dict:
        return self.load_schema("enterprise_orgs")

    def read_records(self, sync_mode: SyncMode, cursor_field=None, stream_slice=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        token = self.get_installation_token_for_target()

        try:
            # First, try to fetch organizations assuming it's an enterprise
            logger.info(f"Attempting to fetch organizations from enterprise '{self.org_or_enterprise}'...")
            enterprise_orgs = f"https://api.github.com/enterprises/{self.org_or_enterprise}/organizations"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
            orgs = paginate_github(enterprise_orgs, headers)
            for org in orgs:
                logger.debug(f"Emitting org record from enterprise: {org.get('login', 'unknown')}")
                yield org

        except Exception as e:
            # If enterprise request fails, assume it's a single organization
            logger.info(f"Entity '{self.org_or_enterprise}' is not an enterprise, treating as single organization")

            # Fetch single organization data
            org_data = f"https://api.github.com/orgs/{self.org_or_enterprise}"
            try:
                org_response = requests.get(org_data, headers=headers)
                org_response.raise_for_status()
                org_data = org_response.json()
                logger.debug(f"Emitting single org record: {self.org_or_enterprise}")
                yield org_data
            except Exception as org_error:
                logger.error(f"Failed to fetch organization data: {org_error}")
                yield {"login": self.org_or_enterprise}


class OrgMembersStream(BaseGithubStream):
    """
    Lists members of each organization provided by ParentOrgsStream.
    """

    name = "org_members"  # <-- class-level attribute

    def get_json_schema(self) -> dict:
        return self.load_schema("org_members")

    def stream_slices(self, sync_mode: SyncMode, cursor_field=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        logger.debug("Generating slices for org_members from parent orgs...")
        parent = ParentOrgsStream(self.app_id, self.private_key, self.org_or_enterprise, self.is_enterprise)
        for org_record in parent.read_records(sync_mode=sync_mode):
            org_login = org_record["login"]
            logger.debug(f"Yielding slice for org: {org_login}")
            yield org_record

    def read_records(self, sync_mode: SyncMode, cursor_field=None, stream_slice=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        if stream_slice is None:
            logger.debug("No stream_slice provided for org_members, yielding no records.")
            return

        org_name = stream_slice["login"]
        logger.info(f"Listing members for organization '{org_name}'...")
        token = self.get_installation_token_for_target()
        url = f"https://api.github.com/orgs/{org_name}/members?per_page=100"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        members = paginate_github(url, headers)
        logger.info(f"Found {len(members)} members in org '{org_name}'.")

        for member in members:
            member_login = member.get("login")
            logger.debug(f"Emitting member record: {member_login} in org '{org_name}'")
            yield member


class OrgReposStream(BaseGithubStream):
    """
    Lists repositories for each organization provided by ParentOrgsStream.
    """

    name = "org_repos"  # <-- class-level attribute

    def get_json_schema(self) -> dict:
        return self.load_schema("org_repos")

    def stream_slices(self, sync_mode: SyncMode, cursor_field=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        logger.debug("Generating slices for org_repos from parent orgs...")
        parent = ParentOrgsStream(self.app_id, self.private_key, self.org_or_enterprise, self.is_enterprise)
        for org_record in parent.read_records(sync_mode=sync_mode):
            org_login = org_record["login"]
            logger.debug(f"Yielding slice for repos in org: {org_login}")
            yield org_record

    def read_records(self, sync_mode: SyncMode, cursor_field=None, stream_slice=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            logger.debug("No stream_slice provided for org_repos, yielding no records.")
            return

        org_name = stream_slice["login"]
        logger.info(f"Listing repositories for organization '{org_name}'...")
        token = self.get_installation_token_for_target()
        url = f"https://api.github.com/orgs/{org_name}/repos?type=all&per_page=100"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        repos = paginate_github(url, headers)
        logger.info(f"Found {len(repos)} repositories in org '{org_name}'.")

        for repo in repos:
            repo_name = repo["name"]
            logger.debug(f"Emitting repository record: {repo_name} in org '{org_name}'")
            yield repo


class RepoCollaboratorsStream(BaseGithubStream):
    """
    Lists collaborators for each repository retrieved from OrgReposStream.
    """

    name = "repo_collaborators"  # <-- class-level attribute

    def get_json_schema(self) -> dict:
        return self.load_schema("repo_collaborators")

    def stream_slices(self, sync_mode: SyncMode, cursor_field=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        logger.debug("Generating slices for repo_collaborators from parent orgs...")
        parent = ParentOrgsStream(self.app_id, self.private_key, self.org_or_enterprise, self.is_enterprise)
        for org_record in parent.read_records(sync_mode=sync_mode):
            org_name = org_record["login"]
            logger.info(f"Listing repositories for organization '{org_name}'...")
            token = self.get_installation_token_for_target()
            url = f"https://api.github.com/orgs/{org_name}/repos?type=all&per_page=100"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
            repos = paginate_github(url, headers)
            logger.info(f"Found {len(repos)} repositories in org '{org_name}'.")

            for repo_record in repos:
                repo_name = repo_record["name"]
                logger.debug(f"Emitting repository record: {repo_name} in org '{org_name}'")
                yield repo_record

    def read_records(self, sync_mode: SyncMode, cursor_field=None, stream_slice=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            logger.debug("No stream_slice provided for repo_collaborators, yielding no records.")
            return

        owner = stream_slice['owner']['login']
        repo = stream_slice['name']

        logger.info(f"Listing collaborators for repo '{owner}/{repo}'")
        token = self.get_installation_token_for_target()

        url = f"https://api.github.com/repos/{owner}/{repo}/collaborators?per_page=100"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        collaborators = paginate_github(url, headers)
        logger.info(f"Found {len(collaborators)} collaborators in repo '{repo}'")

        for collaborator in collaborators:
            collaborator_login = collaborator.get("login")
            logger.debug(f"Emitting collaborator record: {collaborator_login} for repo '{repo}'")
            collaborator["repo"] = repo
            collaborator["owner"] = owner
            yield collaborator


class AuditLogsStream(BaseGithubStream):
    """
    Incrementally fetches GitHub Audit Logs.
    All timestamps are treated as integer Unix timestamps in milliseconds.
    """

    name = "audit_logs"  # <-- class-level attribute
    cursor_field = "@timestamp"
    primary_key = None
    page_size = 100

    def __init__(self, app_id: int, private_key: str, org_or_enterprise: str, is_enterprise: bool):
        super().__init__(app_id, private_key, org_or_enterprise, is_enterprise)
        self._cursor_value = None

    def get_json_schema(self) -> dict:
        return self.load_schema("audit_logs")

    def supported_sync_modes(self) -> List[SyncMode]:
        return [SyncMode.incremental]

    def get_updated_state(self, current_stream_state: Mapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_state = current_stream_state or {}
        current_cursor = current_state.get(self.cursor_field)
        latest_cursor = latest_record.get(self.cursor_field)
        if current_cursor is None or (latest_cursor is not None and latest_cursor > current_cursor):
            logger.debug(f"Updating state from {current_cursor} to {latest_cursor}")
            return {self.cursor_field: latest_cursor}
        return current_state

    def stream_slices(self, sync_mode: SyncMode, cursor_field=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        logger.debug("Generating single slice for audit_logs stream.")
        yield {}

    def _make_url(self) -> str:
        base = "https://api.github.com"
        if self.is_enterprise:
            return f"{base}/enterprises/{self.org_or_enterprise}/audit-log"
        else:
            return f"{base}/orgs/{self.org_or_enterprise}/audit-log"

    def read_records(self, sync_mode: SyncMode, cursor_field=None, stream_slice=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        token = self.get_installation_token_for_target()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

        start_cursor = self._determine_start_from_state(stream_state)
        logger.info(
            f"Starting audit logs sync from timestamp: {start_cursor}" if start_cursor else "Starting audit logs sync from the beginning")

        url = self._make_url()

        while url:
            logger.debug(f"Requesting: {url}")
            resp = requests.get(url, headers=headers)
            if resp.status_code == 404:
                logger.warning("Audit logs not available.")
                return
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list) or len(data) == 0:
                logger.info("No more data returned.")
                break

            # Filter out records at or before the current cursor
            records = [r for r in data if self._record_is_newer(r, start_cursor)]
            logger.info(f"Emitting {len(records)} records.")
            for record in records:
                ts = record.get("@timestamp")
                if ts is not None:
                    logger.debug(f"Record @timestamp={ts} - {record}")
                    yield record
                    if self._cursor_value is None or ts > self._cursor_value:
                        logger.debug(f"Updating cursor to {ts}")
                        self._cursor_value = ts

            url = self._next_link(resp.headers.get("Link"))

        logger.debug("Audit logs incremental sync complete.")

    def _determine_start_from_state(self, state: Optional[Mapping[str, Any]]) -> Optional[int]:
        if state and self.cursor_field in state:
            val = int(state[self.cursor_field])
            logger.debug(f"Resuming from {val}")
            return val
        logger.debug("No previous state, starting from earliest logs.")
        return None

    def _initial_url(self) -> str:
        # Always fetch from the earliest logs
        base = "https://api.github.com"
        # No enterprise logic, no filtering, just return org-level endpoint
        return f"{base}/orgs/{self.org_or_enterprise}/audit-log?per_page={self.page_size}"

    def _record_is_newer(self, record: dict, start_cursor: Optional[int]) -> bool:
        ts = record.get("@timestamp")
        if ts is None or not isinstance(ts, int):
            return False
        if start_cursor is not None and ts <= start_cursor:
            return False
        return True

    def _next_link(self, link_header: Optional[str]) -> Optional[str]:
        if not link_header:
            logger.debug("No Link header found, no next page.")
            return None
        for part in link_header.split(","):
            if 'rel="next"' in part:
                next_url = part.split(";")[0].strip("<> ")
                logger.debug(f"Found next link: {next_url}")
                return next_url
        logger.debug("No next link found in Link header.")
        return None


class OrgCredentialAuthorizationsStream(BaseGithubStream):
    """
    Lists credential authorizations for an organization.
    This endpoint returns OAuth tokens and SSH keys that have been authorized,
    helping identify non-human identities like PATs and OAuth apps.
    API: GET /orgs/{org}/credential-authorizations
    Docs: https://docs.github.com/en/rest/orgs/orgs#list-credential-authorizations-for-an-organization
    """

    name = "org_credential_authorizations"  # <-- class-level attribute

    def get_json_schema(self) -> dict:
        return self.load_schema("org_credential_authorizations")

    def stream_slices(self, sync_mode: SyncMode, cursor_field=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        # Similar to other org-level streams, we rely on ParentOrgsStream for the org login.
        logger.debug("Generating slices for org_credential_authorizations from parent orgs...")
        parent = ParentOrgsStream(self.app_id, self.private_key, self.org_or_enterprise, self.is_enterprise)
        for org_record in parent.read_records(sync_mode=sync_mode):
            org_login = org_record["login"]
            logger.debug(f"Yielding slice for credential authorizations in org: {org_login}")
            yield org_record

    def read_records(self, sync_mode: SyncMode, cursor_field=None, stream_slice=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            logger.debug("No stream_slice provided for org_credential_authorizations, yielding no records.")
            return

        org_name = stream_slice["login"]
        logger.info(f"Listing credential authorizations for organization '{org_name}'...")
        token = self.get_installation_token_for_target()
        url = f"https://api.github.com/orgs/{org_name}/credential-authorizations"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

        # If this endpoint is paginated in the future, you can switch to paginate_github.
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        credentials = response.json()

        logger.info(f"Found {len(credentials)} credential authorizations in org '{org_name}'.")
        for credential in credentials:
            # Each record represents a credential (like an OAuth token or SSH key).
            logger.debug(
                f"Emitting credential authorization record: "
                f"{credential.get('credential_type')} | {credential.get('login') or credential.get('fingerprint')} | {credential.get('authorized_credential_note')} - {credential}"
            )
            credential["org"] = org_name
            yield credential


class OrgInstallationsStream(BaseGithubStream):
    """
    Lists GitHub App installations for the organization.
    This identifies GitHub Apps (non-human identities) installed in the org.
    API: GET /orgs/{org}/installations
    Docs: https://docs.github.com/en/rest/apps/apps#list-app-installations-for-an-organization
    """

    name = "org_installations"  # <-- class-level attribute

    def get_json_schema(self) -> dict:
        return self.load_schema("org_installations")

    def stream_slices(self, sync_mode: SyncMode, cursor_field=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        logger.debug("Generating slices for org_installations from parent orgs...")
        parent = ParentOrgsStream(self.app_id, self.private_key, self.org_or_enterprise, self.is_enterprise)
        for org_record in parent.read_records(sync_mode=sync_mode):
            org_login = org_record["login"]
            logger.debug(f"Yielding slice for installations in org: {org_login}")
            yield org_record

    def read_records(self, sync_mode: SyncMode, cursor_field=None, stream_slice=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            logger.debug("No stream_slice provided for org_installations, yielding no records.")
            return

        org_name = stream_slice["login"]
        logger.info(f"Listing installations (GitHub Apps) for organization '{org_name}'...")
        token = self.get_installation_token_for_target()
        url = f"https://api.github.com/orgs/{org_name}/installations"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

        # If this endpoint is paginated, switch to paginate_github; otherwise a single request is enough:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # According to docs, this returns a JSON with "installations" key.
        installations = data.get("installations", [])
        logger.info(f"Found {len(installations)} installations (GitHub Apps) in org '{org_name}'.")

        for installation in installations:
            app_id = installation["id"]
            app_name = installation["app_slug"]
            logger.debug(f"Emitting installation record for app: {app_id} | {app_name} - {installation}")
            installation["org"] = org_name
            yield installation

class OrgWebhooksStream(BaseGithubStream):
    """
    Lists organization-level webhooks for each organization provided by ParentOrgsStream.
    """

    name = "org_webhooks"  # <-- class-level attribute

    def get_json_schema(self) -> dict:
        # Load the schema from "org_webhooks.json" in your "schemas" directory
        return self.load_schema("org_webhooks")

    def stream_slices(self, sync_mode: SyncMode, cursor_field=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        logger.debug("Generating slices for org_webhooks from parent orgs...")
        parent = ParentOrgsStream(self.app_id, self.private_key, self.org_or_enterprise, self.is_enterprise)
        for org_record in parent.read_records(sync_mode=sync_mode):
            org_login = org_record["login"]
            logger.debug(f"Yielding slice for org: {org_login}")
            yield org_record

    def read_records(self, sync_mode: SyncMode, cursor_field=None, stream_slice=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        if stream_slice is None:
            logger.debug("No stream_slice provided for org_webhooks, yielding no records.")
            return

        org_name = stream_slice["login"]
        logger.info(f"Listing org-level webhooks for organization '{org_name}'...")
        token = self.get_installation_token_for_target()
        url = f"https://api.github.com/orgs/{org_name}/hooks"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

        webhooks = paginate_github(url, headers)
        logger.info(f"Found {len(webhooks)} org-level webhooks in org '{org_name}'.")

        for webhook in webhooks:
            webhook_id = webhook.get("id")
            logger.debug(f"Emitting org-level webhook record: {webhook_id} in org '{org_name}'")
            # Attach context to the record, if desired
            webhook["org"] = org_name
            yield webhook

class RepoWebhooksStream(BaseGithubStream):
    """
    Lists repository-level webhooks for each repository retrieved from OrgReposStream.
    """

    name = "repo_webhooks"  # <-- class-level attribute

    def get_json_schema(self) -> dict:
        # Load the schema from "repo_webhooks.json" in your "schemas" directory
        return self.load_schema("repo_webhooks")

    def stream_slices(self, sync_mode: SyncMode, cursor_field=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        logger.debug("Generating slices for repo_collaborators from parent orgs...")
        parent = ParentOrgsStream(self.app_id, self.private_key, self.org_or_enterprise, self.is_enterprise)
        for org_record in parent.read_records(sync_mode=sync_mode):
            org_name = org_record["login"]
            logger.info(f"Listing repositories for organization '{org_name}'...")
            token = self.get_installation_token_for_target()
            url = f"https://api.github.com/orgs/{org_name}/repos?type=all&per_page=100"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
            repos = paginate_github(url, headers)
            logger.info(f"Found {len(repos)} repositories in org '{org_name}'.")

            for repo_record in repos:
                repo_name = repo_record["name"]
                logger.debug(f"Emitting repository record: {repo_name} in org '{org_name}'")
                yield repo_record

    def read_records(self, sync_mode: SyncMode, cursor_field=None, stream_slice=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            logger.debug("No stream_slice provided for repo_webhooks, yielding no records.")
            return

        owner = stream_slice["owner"]["login"]
        repo = stream_slice["name"]

        logger.info(f"Listing repo-level webhooks for '{owner}/{repo}'...")
        token = self.get_installation_token_for_target()

        url = f"https://api.github.com/repos/{owner}/{repo}/hooks"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

        webhooks = paginate_github(url, headers)
        logger.info(f"Found {len(webhooks)} repo-level webhooks in '{owner}/{repo}'.")

        for webhook in webhooks:
            webhook_id = webhook.get("id")
            logger.debug(f"Emitting repo webhook record: {webhook_id} for '{owner}/{repo}'")
            # Attach context to the record, if desired
            webhook["repo"] = repo
            webhook["owner"] = owner
            yield webhook

class RepoWorkflowRunsStream(BaseGithubStream):
    """
    Lists all workflow runs (GitHub Actions executions) for each repository
    from the OrgReposStream, and includes all the steps for each run.
    """

    name = "repo_workflow_runs"  # Stream name used to identify in code/tests

    # (Optional) If you maintain JSON schemas, ensure you have a
    # repo_workflow_runs.json in your schemas folder
    def get_json_schema(self) -> dict:
        return self.load_schema("repo_workflow_runs")

    def stream_slices(self, sync_mode: SyncMode, cursor_field=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        logger.debug("Generating slices for repo_collaborators from parent orgs...")
        parent = ParentOrgsStream(self.app_id, self.private_key, self.org_or_enterprise, self.is_enterprise)
        for org_record in parent.read_records(sync_mode=sync_mode):
            org_name = org_record["login"]
            logger.info(f"Listing repositories for organization '{org_name}'...")
            token = self.get_installation_token_for_target()
            url = f"https://api.github.com/orgs/{org_name}/repos?type=all&per_page=100"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
            repos = paginate_github(url, headers)
            logger.info(f"Found {len(repos)} repositories in org '{org_name}'.")

            for repo_record in repos:
                repo_name = repo_record["name"]
                logger.debug(f"Emitting repository record: {repo_name} in org '{org_name}'")
                yield repo_record

    def read_records(self, sync_mode: SyncMode, cursor_field=None, stream_slice=None, stream_state=None) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            logger.debug("No stream_slice provided for repo_workflow_runs, yielding no records.")
            return

        owner = stream_slice["owner"]["login"]
        repo = stream_slice["name"]

        logger.info(f"Fetching workflow runs for repo: {owner}/{repo}")
        token = self.get_installation_token_for_target()

        runs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

        # 1. Get all workflow runs for the repo
        workflow_runs = paginate_github(runs_url, headers)
        logger.info(f"Found {len(workflow_runs)} workflow runs in {owner}/{repo}")

        # 2. For each run, fetch its jobs (and thereby steps)
        for run in workflow_runs:
            run_id = run["id"]
            logger.debug(f"Fetching jobs for workflow run_id={run_id} in {owner}/{repo}")

            jobs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
            jobs_response = requests.get(jobs_url, headers=headers)
            jobs_response.raise_for_status()
            jobs_data = jobs_response.json()
            # jobs_data is typically {"total_count": X, "jobs": [...]}

            # We only want the list of jobs
            jobs = jobs_data.get("jobs", [])

            # Each job contains a "steps" array with details about each step
            # If you want them all in one record, attach them to the run
            run["jobs"] = jobs

            # Add some extra context fields to the record, if desired
            run["owner"] = owner
            run["repo"] = repo

            yield run
