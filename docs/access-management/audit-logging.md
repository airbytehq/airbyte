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
## Log format

This is a sample of an individual log file.

```json title="<yyyyMMddHHmmss>_<hostname>_<random UUID>.json"
"events": [
    {
      "timestamp": 1737070174216,
      "message": "Logging audit entry: AuditLogEntry(id=4841f1d8-7fa0-416f-8991-4ca521cbb383, timestamp=1737070174212, user=User(userId=bdfe1362-e3e6-4a7b-9db5-a724f6ece6f2, email=alex@example.com, ipAddress=192.168.50.253, userAgent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36), actionName=updatePermission, summary={\"targetUser\":{\"id\":\"424f2c4f-18a7-4bcc-a71a-e84894eadaa7\",\"email\":null},\"targetScope\":{\"type\":\"organization\",\"id\":\"00000000-0000-0000-0000-000000000000\"},\"previousRole\":\"organization_member\",\"newRole\":\"organization_editor\"}, success=true, errorMessage=null)",
      "level": "INFO",
      "logSource": "platform",
      "caller": {
        "className": "io.airbyte.audit.logging.AuditLoggingInterceptor",
        "methodName": "logAuditInfo$io_airbyte_airbyte_audit_logging",
        "lineNumber": 135,
        "threadName": "io-executor-thread-10"
      },
      "throwable": null
    }
]
```

<!-- ### Processing example: should add a couple of samples in Python, etc. -->
