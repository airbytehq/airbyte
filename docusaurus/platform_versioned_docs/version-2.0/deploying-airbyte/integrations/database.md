---
products: oss-community, oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# External Database

For production deployments, we recommend using a dedicated database instance for better reliability, and backups (such as AWS RDS or GCP Cloud SQL) instead of the default internal Postgres database (`airbyte/db`) that Airbyte spins up within the Kubernetes cluster.

The following instructions assume that you've already configured a Postgres instance:

## Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-config-secrets
type: Opaque
stringData:
  # Database Secrets
  database-user: ## e.g. airbyte
  database-password: ## e.g. password
```

## Values

Add external database details to your `values.yaml` file. This disables the default internal Postgres database (`airbyte/db`), and configures your external Postgres database. You can override all of the values below by setting them in the airbyte-config-secrets or set them directly in the `values.yaml` file. **The database password is a special case in that it must be set in the [airbyte-config-secrets](#secrets).**

<Tabs groupId="helm-chart-version">
<TabItem value='helm-1' label='Helm chart V1' default>

```yaml title="values.yaml"
postgresql:
  enabled: false

global:
  database:
    type: external

    # -- Secret name where database credentials are stored
    secretName: "" # e.g. "airbyte-config-secrets"

    # -- The database host
    host: ""

    # -- The database port
    port: ""

    # -- The database name
    database: ""

    # -- The key within `secretName` where database user is stored
    userSecretKey: "" # e.g. "database-user"

    # -- The key within `secretName` where password is stored
    passwordSecretKey: "" # e.g."database-password"
```

</TabItem>
<TabItem value='helm-2' label='Helm chart V2' default>

```yaml title="values.yaml"
postgresql:
  enabled: false

global:
  database:
    type: external

    # -- Secret name where database credentials are stored
    secretName: "" # e.g. "airbyte-config-secrets"

    # -- The database host
    host: ""

    # -- The database port
    port: ""

    # -- The database name
    name: ""

    # -- The key within `secretName` where database user is stored
    userSecretKey: "" # e.g. "database-user"

    # -- The key within `secretName` where password is stored
    passwordSecretKey: "" # e.g."database-password"
```

</TabItem>
</Tabs>
