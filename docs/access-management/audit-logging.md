---
products: oss-enterprise
---

# Audit logging

Audit logging provides you with full visibility into permission changes for role based access control (RBAC) roles. This data ensures you have records of any unauthorized changes and insider threats, making it easy to continue meeting your compliance obligations while using Airbyte.

## How it works

Create a blob storage solution to store audit logs. Then, use Airbyte's `values.yaml` file to configure that storage solution. Once enabled, audit logs are written to the `/audit-logging/` directory as JSON files. These files have the following naming convention: `<yyyyMMddHHmmss>_<hostname>_<random UUID>`. You can process these logs outside of Airbyte using any tool you like.

## Step 1: Configure blob storage

Create a new blob storage bucket with your chosen cloud provider (for example, AWS S3, GCS, or Azure Blob Storage). This must be a separate bucket from that used for log and state storage.

## Step 2: Configure audit logging in Airbyte

Configure Airbyte to read from and write to that bucket by modifying your `values.yaml` file.

```yml title="values.yaml"
server:
  env_vars:
    AUDIT_LOGGING_ENABLED: true
    STORAGE_BUCKET_AUDIT_LOGGING: # your-audit-logging-bucket
```

<!-- ## Log format and how to process data

### File system

### Log format

### Processing example -->
