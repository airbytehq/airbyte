
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# State and Logging Storage

For Self-Managed Enterprise deployments, we recommend spinning up standalone log storage for additional reliability using tools such as S3 and GCS instead of against using the default internal Minio storage (`airbyte/minio`). It's then a common practice to configure additional log forwarding from external log storage into your observability tool.

<details open >
<summary>External log storage setup steps</summary>

Add external log storage details to your `values.yaml` file. This disables the default internal Minio instance (`airbyte/minio`), and configures the external log database:

<Tabs >
<TabItem value="S3" label="S3" default>

Ensure you've already created a Kubernetes secret containing both your S3 access key ID, and secret access key. By default, secrets are expected in the `airbyte-config-secrets` Kubernetes secret, under the `aws-s3-access-key-id` and `aws-s3-secret-access-key` keys. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets).

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

Ensure you've already created a Kubernetes secret containing the credentials blob for the service account to be assumed by the cluster. By default, secrets are expected in the `gcp-cred-secrets` Kubernetes secret, under a `gcp.json` file. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets).

```yaml
global:
  storage:
    type: "GCS"
    storageSecretName: gcp-cred-secrets
    bucket: ## GCS bucket names that you've created. We recommend storing the following all in one bucket.
      log: airbyte-bucket
      state: airbyte-bucket
      workloadOutput: airbyte-bucket
    gcs:
      projectId: <project-id>
      credentialsPath: /secrets/gcs-log-creds/gcp.json
```

</TabItem>
<TabItem value="Azure" label="Azure blob store">

Ensure you've already created a Kubernetes secret containing the credentials blob for the service account to be assumed by the cluster. By default, secrets are expected in the `gcp-cred-secrets` Kubernetes secret, under a `gcp.json` file. Steps to configure these are in the above [prerequisites](#configure-kubernetes-secrets).

```yaml
global:
  storage:
    type: "GCS"
    storageSecretName: gcp-cred-secrets
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
</details>
