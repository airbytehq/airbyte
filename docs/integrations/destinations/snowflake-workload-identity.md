# Snowflake workload identity federation

Workload identity federation authenticates the Snowflake destination using the identity of the connector workload instead of a stored Snowflake password or private key. Snowflake maps the workload identity to a service user and applies that user's role grants and authentication policies.

Configure both the [Snowflake service user](https://docs.snowflake.com/en/user-guide/workload-identity-federation) and the identity source in the destination workload before setting up the destination. The database, warehouse, schema, role, and network requirements in the [Snowflake destination guide](./snowflake.md) still apply.

## Choosing a provider

Choose the provider based on the identity Snowflake should trust, not simply where the connector runs. In particular, `AWS` is not limited to instance metadata, and `AZURE` does not use the same credential-discovery mechanism as `AWS`.

| Authentication setup | Provider | Identity and credential path |
| --- | --- | --- |
| AKS or EKS: authenticate directly as a Kubernetes service account | `OIDC` | Snowflake trusts the cluster's OIDC issuer and service-account subject. The connector reads a projected JWT file. No intermediate AWS IAM role or Azure managed identity is required. |
| EKS: authenticate as an IAM role through IRSA | Not supported in this connector release | The bundled AWS SDK is below the documented IRSA minimum. Use `OIDC` for direct EKS service-account authentication. See [AWS SDK compatibility](#aws-sdk-compatibility). |
| EC2: authenticate as the instance-profile IAM role | `AWS` | The AWS credential chain obtains temporary role credentials from EC2 instance metadata. Snowflake trusts the IAM identity. |
| Azure VM or Azure Functions: authenticate as a managed identity | `AZURE` | The driver requests an Entra token from the managed-identity endpoint. Snowflake trusts that Entra identity. |
| AKS: exchange a projected token through Entra Workload Identity | Not supported by `AZURE` | The driver does not exchange `AZURE_FEDERATED_TOKEN_FILE` for an Entra token. Use `OIDC` for direct Kubernetes service-account authentication. |
| Google Cloud: authenticate as a Google service account through the metadata service | `GCP` | The driver requests a Google-signed identity token from the metadata service. The endpoint must expose the intended workload identity to the connector. |
| Another OIDC issuer supplies a rotating JWT file | `OIDC` | Snowflake trusts that issuer, subject, and audience. The runtime acquires and rotates the file; the connector does not request tokens from arbitrary issuer APIs. |

For direct Kubernetes authentication, use `OIDC` on either AKS or EKS. Snowflake validates the cluster issuer and service-account subject directly, without an AWS STS or Entra token exchange. IRSA is not a supported deployment for this connector release; do not select `AWS` on EKS on the assumption that the pod's IAM role is supported.

The native `AWS` provider uses the driver's default credential chain. Environment credentials, Java system properties, and credential profiles can take precedence over an instance profile. Do not inject static access keys when the intended identity is the EC2 instance role. Set `AWS_REGION` explicitly when EC2 metadata is unavailable for region discovery.

IRSA's token normally targets `sts.amazonaws.com`. Direct Snowflake authentication requires the audience configured for the Snowflake service user. Likewise, an AKS token targeting `api://AzureADTokenExchange` is not interchangeable with the direct Snowflake token. A pod can have separate projected tokens for separate audiences.

## Configuring through the Airbyte UI

1. Open the Snowflake destination's setup or edit form. Enter the host, username, warehouse, database, schema, and role. The username is the Snowflake service user whose workload identity you configured, not the Kubernetes service-account name.
2. Set **Authorization Method** to **Workload Identity Federation** and configure the fields below.
3. Run a destination connection check.

| UI field | Configuration key | Value |
| --- | --- | --- |
| Workload Identity Provider | `workload_identity_provider` | Required: `OIDC`, `AWS`, `AZURE`, or `GCP`. See [Choosing a provider](#choosing-a-provider). |
| OIDC Token File Path | `token_file_path` | Required for `OIDC`: an absolute path inside the destination connector container, such as `/var/run/secrets/snowflake/token`. Leave unset for other providers. This is a path, not a token upload. |
| Microsoft Entra Resource | `entra_resource` | Optional for `AZURE`: override the resource requested from the managed-identity endpoint. Leave unset to use the driver's default Snowflake resource. Leave unset for other providers. |

The token-path and Entra-resource fields may appear under **Optional fields** because they do not apply to every provider. For OIDC, expand that section and supply a token path. The connector rejects OIDC configurations without a path, a non-empty token path for other providers, or an Entra resource for a non-Azure provider. When switching providers, clear fields that no longer apply.

The destination form selects the authentication mechanism; it does not provision identities or mount token files. Snowflake trust and grants, service accounts, projected volumes, and provider-specific environment variables or metadata access must be configured separately for the actual destination **check and sync** workloads. Configuring only the Airbyte controller or worker pod is insufficient.

Do not enter a Snowflake password, private key, or short-lived JWT when configuring workload identity federation.

## JSON configuration

The equivalent configuration for OIDC is:

```json
{
  "host": "org-account.snowflakecomputing.com",
  "role": "AIRBYTE_ROLE",
  "warehouse": "AIRBYTE_WAREHOUSE",
  "database": "AIRBYTE_DATABASE",
  "schema": "PUBLIC",
  "username": "AIRBYTE_WIF_USER",
  "credentials": {
    "auth_type": "Workload Identity Federation",
    "workload_identity_provider": "OIDC",
    "token_file_path": "/var/run/secrets/snowflake/token"
  }
}
```

Do not put tokens, passwords, private keys, authenticator overrides, or user/account overrides in `jdbc_url_params`. Workload identity authentication rejects these conflicting parameters.

Workload identity requires HTTPS and a hostname under `snowflakecomputing.com`, `snowflakecomputing.cn`, or `snowflakecomputing.mil`, including PrivateLink names. Use the Snowflake hostname, not a custom DNS alias, IP address, or local emulator. A bare hostname or an `https://` prefix is accepted; an `http://` prefix is rejected. An explicit `ssl` setting must be `true`. Host, port, protocol, and server URL overrides in JDBC parameters are rejected. These checks run in the connector before token-file reads or native cloud attestation, not only in the Airbyte form. Underscores in account hostnames remain supported and are handled by the JDBC driver. Other JDBC options continue to work.

## Kubernetes / AKS or EKS: direct OIDC federation

### 1. Configure Snowflake's trust

Enable the cluster's OIDC issuer and obtain its exact issuer URL, including any trailing slash. Snowflake must be able to retrieve the issuer's OIDC discovery document and signing keys. Use the namespace and service account of the destination connector workload.

Create a dedicated Snowflake service user with a role that has the [Snowflake destination permissions](./snowflake.md). Replace the placeholders in this example:

```sql
CREATE USER AIRBYTE_WIF_USER
  TYPE = SERVICE
  WORKLOAD_IDENTITY = (
    TYPE = OIDC
    ISSUER = '<exact-cluster-oidc-issuer-url>'
    SUBJECT = 'system:serviceaccount:airbyte:airbyte-snowflake'
    OIDC_AUDIENCE_LIST = ('https://org-account.snowflakecomputing.com')
  )
  DEFAULT_ROLE = AIRBYTE_ROLE;

GRANT ROLE AIRBYTE_ROLE TO USER AIRBYTE_WIF_USER;
```

Use the identical audience in the projected token below. The example scopes the audience to a Snowflake account. Snowflake also supports the shared default audience `snowflakecomputing.com`.

### 2. Project a rotating token into the connector container

Apply the following pod-spec fragment to both destination check and destination sync workloads using workload-launcher configuration or a narrowly scoped admission policy. Adapt the container name to the generated pod and preserve its image, command, arguments, volumes, and other settings. This is a pod-spec fragment, not an Airbyte Helm values file.

```yaml
spec:
  serviceAccountName: airbyte-snowflake
  containers:
    - name: destination
      volumeMounts:
        - name: snowflake-identity
          mountPath: /var/run/secrets/snowflake
          readOnly: true
  volumes:
    - name: snowflake-identity
      projected:
        sources:
          - serviceAccountToken:
              audience: https://org-account.snowflakecomputing.com
              expirationSeconds: 3600
              path: token
```

The service account must exist in the job's namespace. Mount the projected directory without `subPath` and ensure the connector's user can read the token. Do not mount the token in unrelated containers or expose this identity to untrusted destinations. Projecting this token does not require granting additional Kubernetes API permissions.

The connector rereads the token path whenever Hikari creates a new physical JDBC connection, following Kubernetes' atomically rotated symlinks. Borrowing an existing pooled connection does not reread the token. The driver and Snowflake manage established sessions; Kubernetes issues and rotates the projected tokens. Missing, unreadable, malformed, or oversized token files cause new connection attempts to fail rather than reuse the previous token.

### 3. Validate the deployment

Run a destination connection check and a small sync. Verify that Snowflake uses the expected service user and that new physical connections succeed after token rotation. Incorrect issuer, subject, audience, or an expired token must fail authentication.

## Provider requirements and limitations

The connector uses Snowflake JDBC **3.26.1** for native cloud attestation. The selected identity source and any required environment variables or metadata endpoints must be available to the destination connector container. The connector does not fall back to a Snowflake password when workload identity authentication fails.

### AWS SDK compatibility

**IRSA is not supported in this connector release.** The Snowflake driver and explicit STS dependency use AWS SDK **1.12.655**, below AWS's [documented Java SDK minimum for IRSA](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts-minimum-sdk.html) of **1.12.782**. The presence of the web-identity provider or STS classes is only a packaging prerequisite, not validation of token exchange or refresh. Supporting IRSA requires aligned AWS SDK dependencies and end-to-end credential-exchange and refresh validation. Use `OIDC` for direct EKS service-account authentication without relying on that credential chain. EKS Pod Identity is a separate mechanism and is not claimed as supported either.

### Azure

`AZURE` uses the driver's Azure VM or Azure Functions managed-identity endpoint flow. It does not use `DefaultAzureCredential` and does not exchange `AZURE_FEDERATED_TOKEN_FILE` through Entra Workload Identity. Use `OIDC` for direct AKS service-account authentication. The optional `entra_resource` maps to the JDBC property `workloadIdentityEntraResource`.

### Google Cloud

`GCP` requires the Google metadata identity-token endpoint. A Google credentials file alone is insufficient. Configure the metadata service to expose the intended Google service-account identity to the destination workload.

## References

- [Snowflake workload identity federation](https://docs.snowflake.com/en/user-guide/workload-identity-federation)
- [Snowflake JDBC parameters](https://docs.snowflake.com/en/developer-guide/jdbc/jdbc-parameters)
- [AWS IRSA credential flow and SDK requirements](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts-minimum-sdk.html)
- [Snowflake JDBC 3.26.1 workload identity implementation](https://github.com/snowflakedb/snowflake-jdbc/tree/v3.26.1/src/main/java/net/snowflake/client/core/auth/wif)
