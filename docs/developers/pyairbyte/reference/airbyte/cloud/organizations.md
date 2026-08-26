---
id: airbyte-cloud-organizations
title: airbyte.cloud.organizations
---

PyAirbyte classes and methods for Airbyte Cloud organizations.

### `CloudOrganization` {#airbyte.cloud.organizations.CloudOrganization}

<ApiMember kind="class">

<ApiSignature>

```python
class CloudOrganization(
    organization_id: str,
    organization_name: str | None = None,
    email: str | None = None,
    *,
    client_id: str | SecretString | None = None,
    client_secret: str | SecretString | None = None,
    bearer_token: str | SecretString | None = None,
    public_api_root: str | None = None,
    config_api_root: str | None = None,
)
```

</ApiSignature>

Information about an organization in Airbyte Cloud.

This class provides lazy loading of organization attributes including billing status.
It is typically created via `CloudWorkspace.get_organization()`.

Initialize a `CloudOrganization`.

#### Attributes {#airbyte.cloud.organizations.CloudOrganization--attributes}

- **`email`**&nbsp;(`str | None`) — Email associated with the organization.

- **`is_account_locked`**&nbsp;(`bool`) — Whether the account is locked due to billing issues.

- **`organization_id`** — The organization ID.

- **`organization_name`**&nbsp;(`str | None`) — Display name of the organization.

- **`payment_status`**&nbsp;(`str | None`) — Payment status of the organization.

- **`subscription_status`**&nbsp;(`str | None`) — Subscription status of the organization.

</ApiMember>