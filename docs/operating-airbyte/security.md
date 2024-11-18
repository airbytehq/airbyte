---
products: all
---

# Security

Airbyte is committed to keeping your data safe by following industry-standard practices for securing physical deployments, setting access policies, and leveraging the security features of leading Cloud providers.

If you have any security concerns with Airbyte or believe you have uncovered a vulnerability, contact us at [security@airbyte.io](mailto:security@airbyte.io)

## Securing your data

Airbyte connectors operate as the data pipes moving data from Point A to point B: Extracting data from data sources (APIs, files, databases) and loading it into destination platforms (warehouses, data lakes) with optional transformation performed at the data destination. As soon as data is transferred from the source to the destination, it is purged from an Airbyte deployment.

An Airbyte deployment stores the following data:

### Technical Logs

Technical logs are stored for troubleshooting purposes and may contain sensitive data based on the connection’s `state` data. If your connection is set to an Incremental sync mode, users choose which column is the cursor for their connection. While we strongly recommend a timestamp like an `updated_at` column, users can choose any column they want to be the cursor.

### Configuration Metadata

Airbyte retains configuration details and data points such as table and column names for each integration.

### Sensitive Data​

As Airbyte is not aware of the data being transferred, users are required to follow the [Terms of Services](https://airbyte.com/terms) and are ultimately responsible for ensuring their data transfer is compliant with their jurisdiction.

For more information, see [Airbyte’s Privacy Policy](https://airbyte.com/privacy-policy)

## Securing Airbyte Open Source

:::note
In version 0.44.0, Airbyte Open Source runs a security self-check during setup to help users secure their Airbyte instance. The security self-check verifies whether the instance is accessible from the internet and if strong authentication is configured.

Our security and reliability commitments are only applicable to Airbyte Cloud. Airbyte Open Source security and reliability depend on your development and production setups.
:::

### Network Security

Deploy Airbyte Open Source in a private network or use a firewall to filter which IP addresses are allowed to access your host. Airbyte Open Source currently does not include any user management or role-based access controls (RBAC) to prevent unauthorized access to the API or UI. Controlling who has access to the hardware and network your Airbyte deployment runs on is your responsibility.

You can secure access to Airbyte using the following methods:

- Deploy Airbyte in a private network or use a firewall to filter which IP is allowed to access your host.
- Deploy Airbyte behind a reverse proxy and handle the access control and SSL encryption on the reverse proxy side.
  ```
  # Example nginx reverse proxy config
  server {
    listen 443 ssl;
    server_name airbyte.<your-domain>.com;
    client_max_body_size 200M;  # required for Airbyte API
    ssl_certificate <path-to-your-cert>.crt.pem;
    ssl_certificate_key <path-to-your-key>.key.pem;

    location / {
      proxy_pass http://127.0.0.1:8000;
      proxy_set_header Cookie $http_cookie;  # if you use Airbytes basic auth
      proxy_read_timeout 3600;  # set a number in seconds suitable for you
    }
  }
  ```
- By default, Airbyte generates a secure password during a deploy (either via Helm or `abctl`). To change the default 
password follow the instructions found [here](../deploying-airbyte/integrations/authentication)

- If you deployed Airbyte on a cloud provider:
  - GCP: use the [Identity-Aware proxy](https://cloud.google.com/iap) service
  - AWS: use the [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html) service

### Credential management

To allow you to configure syncs and connectors, Airbyte stores the credentials (like API Keys and passwords) you provide in the Airbyte application database. Make sure you protect the [configuration management routes](https://airbyte-public-api-docs.s3.us-east-2.amazonaws.com/rapidoc-api-docs.html).

If you’re deploying Airbyte Open Source on GCP, you may use Google [Secret Manager](https://cloud.google.com/secret-manager) to store credentials instead of in the database:

1. Create a service account with Google Secret Manager with read/write access. Generate a JSON key.
2. In the Worker and Server applications, set the `SECRET_STORE_GCP_PROJECT_ID` environment variable to the GCP project to which the credentials have access and secrets will be located.
3. In the Worker and Server applications, set the `SECRET_STORE_GCP_CREDENTIALS` environment variable to the JSON key created in step 1.
4. In the Worker and Server applications, set the `SECRET_PERSISTENCE` environment variable to `GOOGLE_SECRET_MANAGER`.

Note that this process is not reversible. Once you have converted to a secret store, you won’t be able to reverse it.

### Encryption

Most Airbyte Open Source connectors support encryption-in-transit (SSL or HTTPS). We recommend configuring your connectors to use the encryption option whenever available.

### Sensitive Data

To facilitate troubleshooting, the Server component may output initial user configurations to the log stream when server loglevel is set to `DEBUG`.
To keep this information private, it is recommended to keep loglevel set to `INFO`  outside of troubleshooting.

## Securing Airbyte Cloud

Airbyte Cloud leverages the security features of leading Cloud providers and sets least-privilege access policies to ensure data security.

### Physical infrastructure

Airbyte Cloud is currently deployed on GCP with all servers located in the United States. We use isolated pods to ensure your data is kept separate from other customers’ data.

Only certain Airbyte staff can access Airbyte infrastructure and technical logs for deployments, upgrades, configuration changes, and troubleshooting.

### Network security

Depending on your [data residency](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-data-residency) location, you may need to allowlist the following IP addresses to enable access to Airbyte:

#### United States and Airbyte Default

GCP region: us-west3

- 34.106.109.131
- 34.106.196.165
- 34.106.60.246
- 34.106.229.69
- 34.106.127.139
- 34.106.218.58
- 34.106.115.240
- 34.106.225.141

#### European Union

AWS region: eu-west-3

- 13.37.4.46
- 13.37.142.60
- 35.181.124.238

### Credential management

Most Airbyte Cloud connectors require keys, secrets, or passwords to allow the connectors to continually sync without prompting credentials on every refresh. Airbyte Cloud fetches credentials using HTTPS and stores them in Google Cloud’s [Secret Manager](https://cloud.google.com/secret-manager). When persisting connector configurations to disk or the database, we store a version of the configuration that points to the secret in Google Secret Manager instead of the secret itself to limit the parts of the system interacting with secrets.

### Encryption

Since Airbyte Cloud only transfers data from source to destination and purges the data after the transfer is finished, data in transit is encrypted with TLS, and no in-store encryption is required for the data. Airbyte Cloud does store [customer metadata](https://docs.google.com/document/d/1bN5NtW57umIcsticFqdhuvSQRfMuGQlijFClFQQFqL8/edit#heading=h.t0xpm320m2ar) and encrypts it using GCP’s encryption service with AES-256-bit encryption keys.

All Airbyte Cloud connectors (APIs, files, databases) pull data through encrypted channels (SSL, SSH tunnel, HTTPS), and the data transfer between our clients' infrastructure and Airbyte infrastructure is fully encrypted.

### Authentication

Airbyte Cloud allows you to log in to the platform using your email and password, Google account, or GitHub account.

### Access Control

Airbyte Cloud supports [user management](/using-airbyte/workspaces.md#add-users-to-your-workspace). 

In addition, Airbyte Cloud and  Airbyte Enterprise support [role-based access control](../access-management/rbac.md) allowing admins to manage varying access levels across users in their instance.

### Compliance

Our compliance efforts for Airbyte Cloud include:

- SOC 2 Type II assessment: An independent third-party completed a SOC2 Type II assessment and found effective operational controls in place. Independent third-party audits will continue at a regular cadence, and the most recent report is available upon request.
- ISO 27001 certification: We received our ISO 27001 certification in November 2022. A copy of the certificate is available upon request.
- Assessments and penetration tests: We use tools provided by the Cloud platforms as well as third-party assessments and penetration tests.

## Reporting Vulnerabilities​

:::warning
Do not file GitHub issues or post on our community Slack or forum for security vulnerabilities since they're public avenues and may lead to additional security concerns.
:::

Airbyte takes security issues very seriously. If you have any concerns about Airbyte or believe you have uncovered a vulnerability, contact us at [security@airbyte.io](mailto:security@airbyte.io). In the message, try to describe the issue and a way to reproduce it. The security team will get back to you as soon as possible.

Use this security address only for undisclosed vulnerabilities. For fixed issues or general questions on how to use the security features, use the [Discourse forum](https://discuss.airbyte.io/) or [Community Slack](https://slack.airbyte.com/).

Please report any security problems to us before disclosing it publicly.
