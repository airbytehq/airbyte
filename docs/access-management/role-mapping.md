---
products: oss-enterprise, cloud-teams
---

# RBAC Role Mapping

Role-Based Access Control (RBAC) role mapping allows automatic assignment of specific permissions to Airbyte users based on existing roles in your organization. It ensures users have appropriate Airbyte access without manual oversight. RBAC functionality is only available in Airbyte Teams and Self-Managed Enterprise.

Enabling role mapping in Airbyte requires use of the Airbyte API. The Airbyte API exposes endpoints that allow you to retrieve and update user permissions. These endpoints can be used to build automation that manages user access to different workspaces. This functionality is currently limited to the Airbyte API, and is not available in the Terraform Provider.

To enable the Airbyte API in Airbyte Teams or Self-Managed Enterprise, follow these [prerequisites](../enterprise-setup/api-access-config.md).

## Relevant API Endpoints

Organization-wide permissions and each set of workspace permissions each count as their own permission object. For example, if an Airbyte user is an 'Organization Member' and has 'Workspace Editor' access in 3 distinct workspaces, this user has 4 permissions in total.

1. [Get a list of current Airbyte users in your organization](https://reference.airbyte.com/reference/listuserswithinanorganization).
2. [Get a list of current Airbyte workspaces](https://reference.airbyte.com/reference/listworkspaces).
2. [Create a permission for an Airbyte user to access to a new workspace](https://reference.airbyte.com/reference/createpermission).
3. [Get a list of a user's current permissions](https://reference.airbyte.com/reference/listpermissions).
3. [Modify permission scope or level of access](https://reference.airbyte.com/reference/updatepermission).
4. [Delete a permission](https://reference.airbyte.com/reference/deletepermission).

## Script Example

### Prerequisites

1. A mapping of user emails to your company-specific roles (e.g. `finance-team`, `security-team`, `us-employee`, etc.):

```yaml
{ 
"user1@company.com": ["companyGroup1", "companyGroup2"], 
"user1@company.com": ["companyGroup2", "companyGroup3"] 
}
```

2. A mapping of your company-specific roles to desired Airbyte permissions:

```yaml
{
  "companyGroup1": [
    {
      "scope": "workspace",
      "scopeId": "workspace1",
      "permissionType": "workspace_admin"
    },
    {
      "scope": "workspace",
      "scopeId": "workspace2",
      "permissionType": "workspace_reader"
    }
  ],
  "companyGroup2": [
    {
      "scope": "workspace",
      "scopeId": "workspace1",
      "permissionType": "workspace_reader"
    }
  ]
}
```
Notes:
- `scope` must be set to either 'workspace' or 'organization'.
- `permissionType` must be set to a valid value, e.g. 'workspace_admin', 'workspace_reader', 'organization_admin', etc. All valid values are listed [here](https://github.com/airbytehq/airbyte-api-python-sdk/blob/main/src/airbyte_api/models/publicpermissiontype.py).

### Complete Python Script

Below is an example Python script using the above prerequisite files and the `airbyte-api` Python package to set user roles programmatically:

<details>
<summary>RBAC Role Mapping Python Example</summary>

```python
import json
import airbyte_api
from airbyte_api import api, models

usersGroupsFile = open('usersGroups.json')
usersGroups = json.load(usersGroupsFile)
groupPermissionsFile = open('groupPermissions.json')
groupPermissions = json.load(groupPermissionsFile)

# 0. - Enter your own credentials to use Airbyte API. 
s = airbyte_api.AirbyteAPI(
  security=models.Security(
    bearer_auth='...'
  ),
)

# 1. - List all users in your organization. Find your organization ID in the Airbyte settings page.
res = s.users.list_users(request=api.ListUsersRequest(
  api.ListUsersRequest(organization_id='00000000-00000000-00000000-00000000')
))

allAirbyteUsers = res.users_response.data
print("all users: ", allAirbyteUsers)

# 2. grant permissions
# for each user
for airbyteUserResponse in allAirbyteUsers:
  if airbyteUserResponse.email in usersGroups:
    userGroups = usersGroups[airbyteUserResponse.email]
    # for each group where user belongs to
    for group in userGroups:
      if group in groupPermissions:
        permissionsToGrant = groupPermissions[group]
	 # for each permission to create
        for permission in permissionsToGrant:
          print("permission to grant: ", permission)
          if permission["scope"] == "workspace":
            # create workspace level permission
            permissionCreated = s.permissions.create_permission(
              request=models.PermissionCreateRequest(
                permission_type=permission["permissionType"],
                user_id=airbyteUserResponse.user_id,
                workspace_id=permission["scopeId"]
              ))
          elif permission["scope"] == "organization":
            # create organization permission
            permissionCreated = s.permissions.create_permission(
              request=models.PermissionCreateRequest(
                permission_type=permission["permissionType"],
                user_id=airbyteUserResponse.user_id,
                organization_id=permission["scopeId"]
              ))
          else:
            print("permission scope not supported!")
```

</details>

Please feel free to add your own logging and error-handling workflow in the example script, and you are free to configure it on a CRON job to run at the frequency of your choice.
