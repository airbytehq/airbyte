---
products: oss-community, oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# State and Logging Storage

Airbyte recommends using an object storage solution for such as S3 and GCS for storing [State](../../understanding-airbyte/airbyte-protocol/#state--checkpointing) and [Logging information](../../operator-guides/browsing-output-logs).
You must select which type of blob store that you wish to use. Currently, S3 and GCS are supported. If you are using an S3 compatible solution, use the S3 type and provide an `endpoint` key/value as needed.

Adding external storage details to your `values.yaml` disables the default internal Minio instance (`airbyte/minio`). While there are three separate buckets presented in the Values section below, Airbyte recommends that you use a single bucket across all three values.

## Secrets

<Tabs >
<TabItem value="S3" label="S3" default>

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airbyte-config-secrets
type: Opaque
stringData:
  # AWS S3 Secrets
  s3-access-key-id: ## e.g. AKIAIOSFODNN7EXAMPLE
  s3-secret-access-key: ## e.g. wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

```

</TabItem>
<TabItem value="GCS" label="GCS">

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

<Tabs >
<TabItem value="S3" label="S3" default>

Ensure you've already created a Kubernetes secret containing both your S3 access key ID, and secret access key. By default, secrets are expected in the `airbyte-config-secrets` Kubernetes secret, under the `s3-access-key-id` and `s3-secret-access-key` keys. Steps to configure these are in the above [prerequisites](#secrets).

```yaml
global:
  storage:
    type: "S3"
    storageSecretName: airbyte-config-secrets # Name of your Kubernetes secret.
    bucket: ## S3 bucket names that you've created. We recommend storing the following all in one bucket.
      log: airbyte-bucket
      state: airbyte-bucket
      workloadOutput: airbyte-bucket
    s3:
      region: "" ## e.g. us-east-1
      authenticationType: credentials ## Use "credentials" or "instanceProfile"
```

Set `authenticationType` to `instanceProfile` if the compute infrastructure running Airbyte has pre-existing permissions (e.g. IAM role) to read and write from the appropriate buckets.

</TabItem>
<TabItem value="GCS" label="GCS">

Ensure you've already created a Kubernetes secret containing the credentials blob for the service account to be assumed by the cluster. By default, secrets are expected in the `airbyte-config-secrets` Kubernetes secret, under a `gcp.json` key. Steps to configure these are in the above [prerequisites](#secrets).

```yaml
global:
  storage:
    type: "GCS"
    storageSecretName: airbyte-config-secrets
    bucket: ## GCS bucket names that you've created. We recommend storing the following all in one bucket.
      log: airbyte-bucket
      state: airbyte-bucket
      workloadOutput: airbyte-bucket
    gcs:
      projectId: <project-id>
      credentialsPath: /secrets/gcs-log-creds/gcp.json
```

</TabItem>

</Tabs>
