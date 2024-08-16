---
products: oss-community, oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Secret Management

Secrets are sensitive information that should be kept confidential to protect the security and integrity of your instance.

:::info
Airbyte's default behavior is to store connector secrets on your configured database. This will be stored in plain-text and not encrypted.
:::

Airbyte **highly recommends** storing connector secrets in an external secret manager to ensure secrets are not exposed. The currently supported Secret managers are: AWS Secrets Manager, Google Secrets Manager or Hashicorp Vault. Upon creating a new connector, secrets (e.g. OAuth tokens, database passwords) will be written to and read from the configured Secrets manager.

## Secrets

<Tabs>
<TabItem label="Amazon" value="Amazon" default>

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-config-secrets
type: Opaque
stringData:
  # AWS Secret Manager
  aws-secret-manager-access-key-id: ## e.g. AKIAIOSFODNN7EXAMPLE
  aws-secret-manager-secret-access-key: ## e.g. wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

</TabItem>

<TabItem label="GCP" value="GCP">

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-config-secrets
type: Opaque
stringData:
  gcp.json: ## {
  "type": "service_account",
  "project_id": "cloud-proj",
  "private_key_id": "2f3b9c8e7d5a1b4f23e697c0d84af6e1",
  "private_key": "-----BEGIN PRIVATE KEY-----<REDACTED>\n-----END PRIVATE KEY-----\n",
  "client_email": "cloud-proj.iam.gserviceaccount.com",
  "client_id": "9876543210987654321",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cloud-proj.iam.gserviceaccount.com"
}
```
</TabItem>

</Tabs>

## Values

Modifing the configuration of connector secret storage will cause all <i>existing</i> connectors to fail. You will need to recreate these connectors to ensure they are reading from the appropriate secret store.

<Tabs>
<TabItem label="Amazon" value="Amazon" default>

If authenticating with credentials, ensure you've already created a Kubernetes secret containing both your AWS Secrets Manager access key ID, and secret access key. By default, secrets are expected in the `airbyte-config-secrets` Kubernetes secret, under the `aws-secret-manager-access-key-id` and `aws-secret-manager-secret-access-key` keys. Steps to configure these are in the above [prerequisites](#secrets).

```yaml
global:
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

Ensure you've already created a Kubernetes secret containing the credentials blob for the service account to be assumed by the cluster. By default, secrets are expected in the `airbyte-config-secrets` Kubernetes secret, under a `gcp.json` file. Steps to configure these are in the above [prerequisites](#secrets). For simplicity, we recommend provisioning a single service account with access to both GCS and GSM.

```yaml
global:
  secretsManager:
    type: googleSecretManager
    storageSecretName: gcp-cred-secrets
    googleSecretManager:
      projectId: <project-id>
      credentialsSecretKey: gcp.json
```

</TabItem>
</Tabs>
