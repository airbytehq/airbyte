from typing import Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import *

logger = logging.getLogger("airbyte")


class SourcePulseMicrosoftEntraId(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            token = get_token(config)
            url = f"https://graph.microsoft.com/v1.0/users/delta"
            response = requests.get(
                url=url,
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            Users(config),
            Groups(config),
            Applications(config),
            DirectoryRoles(config),
            ServicePrincipals(config),
            AccessPackages(config),
            AccessPackageResources(config),
            AccessPackageMembers(config),
            DirectoryAudits(config),
            DirectoryRoleTemplates(config),
            AppRolesAssignedTo(config),
            ApplicationOwners(config),
            Catalogs(config),
            DirectoryRolesPermissions(config),
            UserMembershipInGroupsAndDirectory(config)
        ]
