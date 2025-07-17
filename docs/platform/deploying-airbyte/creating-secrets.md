import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Preconfiguring Kubernetes Secrets

Deploying Airbyte requires specifying a number of sensitive values. These can be API keys, usernames and passwords, etc.
In order to protect these sensitive values, the Helm Chart assumes that these values are pre-configured and stored in a Kubernetes Secret *before* the Helm installation begins. Each [integration](#integrations)  will provide the Secret values that are required for the specific integration.

While you can set the name of the secret to whatever you prefer, you will need to set that name in various places in your values.yaml file. For this reason we suggest that you keep the name of `airbyte-config-secrets` unless you have a reason to change it.

<Tabs>
<TabItem value="yaml" label="Creating Secrets with YAML" default>

You can apply your yaml to the cluster with `kubectl apply -f secrets.yaml -n airbyte` to create the secrets.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-config-secrets
type: Opaque
stringData:
  # Examples
  key-1: "value-1"
  key-2: "value-2"
```
</TabItem>

<TabItem value="cli" label="Creating secrets with kubectl">

You can also use `kubectl` to create the secret directly from the CLI:

```sh
kubectl create secret generic airbyte-config-secrets \
  --from-literal=key-1='value-1' \
  --from-literal=key2='value-2' \
  --namespace airbyte
```

</TabItem>
</Tabs>
