# DynamoDB Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 rebuilds the DynamoDB source on Airbyte's Bulk CDK. It reads large tables with [parallel scans](dynamodb.md#concurrency), saves its position during full refresh and incremental syncs so that a large table resumes after an interruption instead of starting over, supports speed mode, reads large numbers exactly, works with integer cursors and reads attributes whose names are reserved words without configuration. Saved configurations that use an access key load unchanged, and the incremental sync state written by versions 0.3.x is understood: a stream resumes after its saved cursor value instead of reading the table again.

**This version removes role based authentication and changes the shape of the stream schemas, so it is a breaking change for the connections described below.**

### Authentication changes

- **Role based authentication is gone.** Versions 0.3.x used the credentials of the environment the connector ran in (an instance role, IRSA, or an AWS profile) when **Access Key ID** and **Secret Access Key** were empty. Version 1.0.0 only uses the credentials in the source configuration. A source configured without an access key fails the connection test with a message that says so.
- **Access Key and IAM Role** is a new authentication method: an access key that is allowed to call `sts:AssumeRole` on an IAM role, the role's ARN and, when the role's trust policy requires one, an external ID. Use it to replace a role based configuration or for cross-account access.
- **Session Token** is a new optional field of the **Access Key** method for temporary credentials issued by AWS STS.
- **AWS Region** is required. Versions 0.3.x accepted an empty value and took the region from the environment.
- **DynamoDB Endpoint**, when set, must be an `http` or `https` URL.

### Schema changes

The schemas of the discovered streams use the same shapes as Airbyte's other database connectors. The attributes and their types don't change, only how the schema writes them.

| Attribute value       | Schema up to 0.3.11                                         | Schema in 1.0.0                                   |
| :-------------------- | :---------------------------------------------------------- | :------------------------------------------------ |
| `S` (string)          | `{"type": ["null", "string"]}`                              | `{"type": "string"}`                              |
| `N` (whole number)    | `{"type": ["null", "integer"]}`                             | `{"type": "number", "airbyte_type": "integer"}`   |
| `N` (other number)    | `{"type": ["null", "number"]}`                              | `{"type": "number"}`                              |
| `B` (binary)          | `{"type": ["null", "string"], "contentEncoding": "base64"}` | `{"type": "string", "contentEncoding": "base64"}` |
| `BOOL`                | `{"type": ["null", "boolean"]}`                             | `{"type": "boolean"}`                             |
| `M` (map)             | `{"type": ["null", "object"], "properties": ...}`           | `{"type": "object", "properties": ...}`           |
| `L`, `SS`, `NS`, `BS` | `{"type": ["null", "array"], "items": ...}`                 | `{"type": "array", "items": ...}`                 |

- An empty table is no longer discovered as a stream, and the connection test fails with `Discovered zero tables.` when the identity can't see any table in the region.
- A connection upgraded from 0.3.x keeps syncing with its saved catalog. Its next schema refresh shows a schema change on every column; the column types in the destination don't change.

### Value changes

- An `N` value that doesn't fit in 64 bits is read as an exact decimal. Versions 0.3.x converted it to a floating point number and lost precision.
- An attribute that an item doesn't have is present in the record as `null`. Versions 0.3.x left it out of the record.
- Incremental syncs on a cursor attribute discovered as `integer` work. Versions 0.3.x failed before the first record.
- Attributes whose names are DynamoDB reserved words or contain special characters are read without listing them in **Reserved attribute names**, which the connector now ignores.

### Other changes

- Full refresh and incremental syncs emit state while they run and resume after an interruption instead of starting over.
- A configured table that no longer exists, or whose stream has no fields, fails only its own stream. Versions 0.3.x failed the whole sync.
- The connection test reports why it failed. Versions 0.3.x reported a failure without a message.

### What to do

1. If a source uses role based authentication (no access key), edit it before or right after the upgrade: choose **Access Key** and enter the access key of an IAM user or temporary credentials with a session token, or choose **Access Key and IAM Role** and enter an access key that may assume the role the connector should read with. See [IAM permissions](dynamodb.md#iam-permissions) for what the identity needs.
2. If **AWS Region** is empty, set it to the region of the tables.
3. Upgrade the connector, then refresh the source schema of each connection that uses it and accept the schema changes. The destination tables and their column types stay as they are.
4. If a sync of an incremental stream on a whole-number cursor failed on 0.3.x, it works on 1.0.0 without a reset.

Nothing else is required. Incremental streams continue from their saved cursor value.
