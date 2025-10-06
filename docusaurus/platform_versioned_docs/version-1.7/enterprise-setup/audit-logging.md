---
products: oss-enterprise
---

# Audit logging

Audit logging gives you visibility into data, environment, user, and permission changes. This data ensures you have records of any unauthorized changes and insider threats, making it easy to continue meeting your compliance obligations while using Airbyte.

## What Airbyte logs

| Event         | Logged operations                                        |
| ------------- | -------------------------------------------------------- |
| Connections   | Create, Update, Delete                                   |
| Sources       | Create, Update, Delete, Partial Update, Upgrade Version  |
| Destinations  | Create, Update, Delete, Partial Update, Upgrade Version  |
| Organizations | Create, Update, Delete                                   |
| Workspaces    | Create, Update, Delete, Update Name, Update Organization |
| Permissions   | Create, Update, Delete                                   |
| Users         | Create, Update, Delete                                   |

## How it works

You set up a blob storage solution to store audit logs. Then, you use Airbyte's `values.yaml` file to configure that storage solution in Airbyte. Once enabled, Airbyte writes audit logs to the `/audit-logging/` directory as JSON files. These files have the following naming convention: `<yyyyMMddHHmmss>_<hostname>_<random UUID>`. You can process these logs outside of Airbyte using any tool you like.

## Log format

Here is an example log for a deleted workspace. Logs for all events follow this same basic format.

```json
{
  "id": "8478fcbd-d369-4bda-8d9b-b782cea5ad40",
  "timestamp": 1746724563299,
  "actor": {
    "actorId": "1c26c465-58h8-43e6-8jko-2252b7g8a9e2",
    "email": "user@airbyte.io",
    "ipAddress": "192.000.000.0",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
  },
  "operation": "deleteWorkspace",
  "request": "<request object>",
  "response": "<response object>",
  "success": true,
  "errorMessage": null
}
```

## Enable logging

### Self-Managed Enterprise

To enable logging, set up a blob storage solution to store audit logs. Then, you use Airbyte's `values.yaml` file to configure that storage solution in Airbyte.

#### Step 1: Configure blob storage

Choose a new blob storage bucket with your chosen cloud provider (for example, AWS S3, GCS, or Azure Blob Storage). This bucket must be accessible by Airbyte's pods using the same credentials it uses to access your log and state storage.

#### Step 2: Configure audit logging in Airbyte

1. Configure Airbyte to read from and write to that bucket by modifying your values.yaml file.

    ```yaml title="values.yaml"
    server:
    env_vars:
        AUDIT_LOGGING_ENABLED: true
        STORAGE_BUCKET_AUDIT_LOGGING: # your-audit-logging-bucket
    ```

2. Redeploy Airbyte.

    ```bash
    helm upgrade \
    --namespace airbyte \
    --values ./values.yaml \
    --install airbyte-enterprise \
    airbyte/airbyte
    ```

### Cloud

Airbyte implements audit logging on all Airbyte Cloud instances. You don't have access to these logs, but the Airbyte team can reference them if you need assistance with a security investigation.
