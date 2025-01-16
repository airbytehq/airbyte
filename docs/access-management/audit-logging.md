---
products: oss-enterprise
---

# Audit logging

Audit logging provides you with full visibility into permission changes for role based access control (RBAC) roles. This data ensures you have records of any unauthorized changes and insider threats, making it easy to continue meeting your compliance obligations while using Airbyte.

## How it works

You set up a blob storage solution to store audit logs. Then, you use Airbyte's `values.yaml` file to configure that storage solution in Airbyte. Once enabled, audit logs are written to the `/audit-logging/` directory as JSON files. These files have the following naming convention: `<yyyyMMddHHmmss>_<hostname>_<random UUID>`. You can process these logs outside of Airbyte using any tool you like.

## Step 1: Configure blob storage

Choose a new blob storage bucket with your chosen cloud provider (for example, AWS S3, GCS, or Azure Blob Storage). This bucket must be accessible by Airbyte's pods using the same credentials it uses to access your log and state storage. It's easiest to reuse your existing bucket, but you can create a new bucket as long as the [authentication is identical](../enterprise-setup/implementation-guide#configuring-external-logging).

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
