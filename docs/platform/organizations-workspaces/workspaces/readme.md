---
products: cloud, oss-enterprise
---

# Workspaces

Each organization consists of one or more **workspaces**. A workspace groups sources, destinations, connections, and other configurations. Workspaces are a more granular layer to manage access, control connections, and monitor usage. You can use a single workspace for everything, or you can divide your organization into multiple workspaces. 

Multiple workspaces are most useful if you're using [Enterprise Flex](../../enterprise-flex/readme) or [Self-Managed Enterprise](../../enterprise-setup/README) and want to self-manage separate data planes, because each workspace runs syncs in a separate region, satisfying data sovereignty and compliance requirements. However, they're also a helpful way to segregate your users into smaller groups who can only access certain data based on their role or permission level in your organization.

Self-Managed Community deployments can only have one workspace.
