import sys
from typing import Any, Mapping, Tuple, Optional, List

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteCatalog, ConnectorSpecification
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.entrypoint import launch

# Import the new GitHubAppStream-based classes:
# (adjust these imports to match your actual file/module structure)
from .streams import (
    ParentOrgsStream,
    OrgMembersStream,
    OrgReposStream,
    RepoCollaboratorsStream,
    AuditLogsStream,
    OrgCredentialAuthorizationsStream,
    OrgInstallationsStream,
    OrgWebhooksStream,
    RepoWebhooksStream,
    RepoWorkflowRunsStream,
    create_jwt,  # if you want to reuse the JWT function here
)

logger = AirbyteLogger()


class SourcePulseGithubApp(AbstractSource):
    """
    The main source class for the Pulse GitHub App connector.
    Uses the new "extra connector" style streams (GitHubAppStream).
    """

    def check_connection(
        self,
        logger: AirbyteLogger,
        config: Mapping[str, Any]
    ) -> Tuple[bool, Optional[Any]]:
        """
        Verifies we can fetch the target org or enterprise installation with just the app-level JWT.
        """
        app_id = config["app_id"]
        private_key = config["private_key"]
        org_or_enterprise = config["org_or_enterprise"]
        is_enterprise = config.get("is_enterprise", False)

        try:
            logger.info("Performing connection check using app-level JWT...")
            jwt_token = create_jwt(app_id, private_key)  # from .streams or your code

            # Fetch all installations at the app level to see if we find a matching org/enterprise
            resp = requests.get(
                "https://api.github.com/app/installations",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github+json"
                }
            )
            resp.raise_for_status()
            installations = resp.json()

            target_type = "Enterprise" if is_enterprise else "Organization"
            matching_installations = [
                i for i in installations
                if i["account"]["login"] == org_or_enterprise
                and i["account"]["type"] == target_type
            ]

            if not matching_installations:
                error_msg = f"No installation found for '{org_or_enterprise}' ({target_type})."
                logger.error(error_msg)
                return False, error_msg

            logger.info("Connection check successful. Found a matching installation.")
            return True, None

        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Any]:
        """
        Return the list of streams that this connector provides.
        These streams inherit from GitHubAppStream (or ParentChildStream).
        """
        app_id = config["app_id"]
        private_key = config["private_key"]
        org_or_enterprise = config["org_or_enterprise"]
        is_enterprise = config.get("is_enterprise", False)

        logger.debug("Creating stream instances for the GitHub connector...")

        return [
            ParentOrgsStream(app_id, private_key, org_or_enterprise, is_enterprise),
            OrgMembersStream(app_id, private_key, org_or_enterprise, is_enterprise),
            OrgReposStream(app_id, private_key, org_or_enterprise, is_enterprise),
            RepoCollaboratorsStream(app_id, private_key, org_or_enterprise, is_enterprise),
            AuditLogsStream(app_id, private_key, org_or_enterprise, is_enterprise),
            OrgCredentialAuthorizationsStream(app_id, private_key, org_or_enterprise, is_enterprise),
            OrgInstallationsStream(app_id, private_key, org_or_enterprise, is_enterprise),
            OrgWebhooksStream(app_id, private_key, org_or_enterprise, is_enterprise),
            RepoWebhooksStream(app_id, private_key, org_or_enterprise, is_enterprise),
            RepoWorkflowRunsStream(app_id, private_key, org_or_enterprise, is_enterprise),
        ]

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """
        Define the configuration spec for this connector, e.g. required fields:
          - app_id
          - private_key
          - org_or_enterprise
          - is_enterprise (optional boolean)
        """
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/sources/github-identities",
            connectionSpecification={
                "type": "object",
                "required": ["app_id", "private_key", "org_or_enterprise"],
                "properties": {
                    "app_id": {
                        "type": "integer",
                        "title": "GitHub App ID",
                        "description": "The ID of your GitHub App."
                    },
                    "private_key": {
                        "type": "string",
                        "title": "GitHub App Private Key (PEM)",
                        "description": "The private key of your GitHub App in PEM format. Provide as a single multiline string.",
                        "airbyte_secret": True,
                        "multiline": True
                    },
                    "org_or_enterprise": {
                        "type": "string",
                        "title": "Organization or Enterprise Slug",
                        "description": "The organization login or enterprise slug you want to target."
                    },
                    "is_enterprise": {
                        "type": "boolean",
                        "default": False,
                        "description": "Set this to true if `org_or_enterprise` is an enterprise slug."
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date-time",
                        "title": "Start Date",
                        "description": "A date/time in ISO8601 format from which to fetch incremental data (e.g., audit logs)."
                    }
                }
            }
        )


if __name__ == "__main__":
    source = SourcePulseGithubApp()
    launch(source, sys.argv[1:])
