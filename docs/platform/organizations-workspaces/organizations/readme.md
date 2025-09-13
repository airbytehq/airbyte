---
products: cloud
---

import DocCardList from '@theme/DocCardList';

# Organizations

The highest level of structure in Airbyte is an **organization**. Organizations are how you manage membership and permissions, billing (if applicable), and overall account usage.

Self-Managed deployments only have one organization, but you can deploy Airbyte multiple times to establish different organizations.

Organizations contain one or more [workspaces](../workspaces). From your organization's home page, you can view all of your workspaces and the current status of all syncs. This is especially useful for identifying workspaces with failed syncs that might need your attention.

![Organization home page](../../images/organization-homepage.png)

Each organization is unrelated to all others. Most Airbyte users belong to a single organization, but some people belong to multiple organizations. For example, a consultant working with multiple companies might have access to multiple Airbyte organizations. Think about the relationship of an organization to a workspace like the following diagram.

```mermaid
flowchart LR
  subgraph Org2[Organization 2]
    direction LR
    WS4[Workspace 4] --- WS5[Workspace 5] --- WS6[Workspace 6]
  end
  subgraph Org1[Organization 1]
    direction LR
    WS1[Workspace 1] --- WS2[Workspace 2] --- WS3[Workspace 3]
  end
```

## Manage your organizations

<DocCardList />
