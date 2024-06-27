
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Secret Management


Airbyte's default behavior is to store encrypted connector secrets on your cluster as Kubernetes secrets. You may <b>optionally</b> opt to instead store connector secrets in an external secret manager such as AWS Secrets Manager, Google Secrets Manager or Hashicorp Vault. Upon creating a new connector, secrets (e.g. OAuth tokens, database passwords) will be written to, then read from the configured secrets manager.

<details open>
<summary>Configuring external connector secret management</summary>

Modifing the configuration of connector secret storage will cause all <i>existing</i> connectors to fail. You will need to recreate these connectors to ensure they are reading from the appropriate secret store.

<Tabs>
<TabItem label="Amazon" value="Amazon">

If authenticating with credentials, ensure you've already created a Kubernetes secret containing both your AWS Secrets Manager access key ID, and secret access key. By default, secrets are expected in the `airbyte-config-secrets` Kubernetes secret, under the `aws-secret-manager-access-key-id` and `aws-secret-manager-secret-access-key` keys. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets).

```yaml
secretsManager:
  type: awsSecretManager
  awsSecretManager:
    region: <aws-region>
    authenticationType: credentials ## Use "credentials" or "instanceProfile"
    tags: ## Optional - You may add tags to new secrets created by Airbyte.
      - key: ## e.g. team
        value: ## e.g. deployments
      - key: business-unit
        value: engineering
    kms: ## Optional - ARN for KMS Decryption.
```

Set `authenticationType` to `instanceProfile` if the compute infrastructure running Airbyte has pre-existing permissions (e.g. IAM role) to read and write from AWS Secrets Manager.

To decrypt secrets in the secret manager with AWS KMS, configure the `kms` field, and ensure your Kubernetes cluster has pre-existing permissions to read and decrypt secrets.

</TabItem>
<TabItem label="GCP" value="GCP">

Ensure you've already created a Kubernetes secret containing the credentials blob for the service account to be assumed by the cluster. By default, secrets are expected in the `gcp-cred-secrets` Kubernetes secret, under a `gcp.json` file. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets). For simplicity, we recommend provisioning a single service account with access to both GCS and GSM.

```yaml
secretsManager:
  type: googleSecretManager
  storageSecretName: gcp-cred-secrets
  googleSecretManager:
    projectId: <project-id>
    credentialsSecretKey: gcp.json
```

</TabItem>
</Tabs>

</details>
