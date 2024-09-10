---
products: oss-enterprise, cloud-teams
---

# Role Based Access Control (RBAC)

Role Based Access Control allows a user with Administrative access to apply roles to users, granting different levels of permission within an Organization or Workspace. 

:::info
**Self-Managed Enterprise** instances have an `Instance Admin` role in addition to the other roles outlined in this document. The first user who logs on to Airbyte in a Self-Managed Enterprise instance will be assigned this role. This user will have all permissions listed below for all workspaces and all organizations associated with their Enterptise account. To update this assigment, enterprise customers should contact [Airbyte support](https://support.airbyte.com/hc/en-us).
:::

## Organization Resource Roles

Permissions are scoped to the given Organization for which the user has this role, and any Workspaces within. 

| Permissions           | Member |  Reader |  Editor | Admin |
| :---------------------- | :--------: | :--------: | :--------: |:--------: |
| **Read Organization**<br /><ul><li> Read individual organizations</li></ul> | X | X | X | X |
| **Create Workspace**<br /><ul><li>Create new workspace within a specified organization</li><li>Delete a workspace</li></ul> | | | X | X |
| **Update Organization**<br /><ul><li>Modify organization settings, including billing, PbA, SSO</li><li>Modify user roles within the organization</li></ul> | |  |  | X |

## Workspace Resource Roles
Permissions are scoped to the specific Workspace in which the user has this role.

| Permissions           | Reader    | Editor    | Admin    |
| ---------------------- | :--------: | :--------:| :--------: |
| **Read Workspace**<br /><ul><li>List the connections in a workspace</li><li>Read individual connections</li><li>Read workspace settings (data residency, users, connector versions, notification settings) </li></ul> | X | X | X |
| **Modify Connector Settings**<br /><ul><li>Create, modify, delete  sources and destinations in a workspace</li></ul> | | X | X |
| **Update Connection**<br /><ul><li> Start/cancel syncs</li><li>Modify a connection, including name, replication settings, normalization, DBT</li><li>Delete a connection</li><li> Create/Update/Delete connector builder connectors</li></ul> |  | X | X |
| **Update Workspace**<br /><ul><li> Update workspace settings (data residency, users, connector versions, notification settings)</li><li> Modify workspace connector versions</li></ul> | |  | X |

## Setting Roles

<Arcade id="pYZ3aHWlV4kJatJG2dJN" title="Organization Permissions" paddingBottom="calc(61.37931034482759% + 41px)" />

In the UI, navigate to `Settings` > `General` to see a list of your Organization or Workspace members. Here, by selecting the role listed under `Organization Role` or `Workspace Role`, you can change the assignment.

Note that it is not possible to assign a Workspace member to a role that is more restricted than the role they've been assigned at the Organizational level. 

For example, a person who is assigned to be an Organization `Admin` would automatically have Admin-level permissions in all Workspaces within the Organization and can not be demoted within a Workspace. On the other hand, a person assigned to the `Reader` role in an Organization could be assigned the `Reader`, `Editor`, or `Admin` role in an individual Workspace.


