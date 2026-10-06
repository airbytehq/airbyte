# SFTP-JSON Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 introduces SSH key authentication alongside the existing password authentication. The connector configuration schema has changed: the top-level `password` field has been replaced by a `credentials` block.

### What changed

| Before (≤ 0.x) | After (1.0.0) |
|:---|:---|
| `"password": "my-secret"` | `"credentials": {"auth_method": "SSH_PASSWORD_AUTH", "auth_user_password": "my-secret"}` |

### Do I need to do anything?

**If you do not interact with the raw connector config:** No. The connector automatically converts legacy `password` configurations to the new `credentials` format at runtime. Your syncs will continue to work.

**If you manage configs programmatically (Terraform, API, etc.):** Update your config to use the new `credentials` block. The legacy `password` field is still accepted but deprecated and will be removed in a future version.

### New features in 1.0.0

- **SSH key authentication**: Connect using an SSH private key (RSA, Ed25519, ECDSA) instead of a password.
- **Host key checking**: Optionally pin the server's SSH host key to protect against man-in-the-middle attacks.

### Host key checking security note

The default host key checking mode (`auto_add`) loads the system's `~/.ssh/known_hosts` file and **rejects** connections to hosts whose keys are not already registered. If connecting to a new host for the first time, you must either:
1. Add the host key to `~/.ssh/known_hosts` via `ssh-keyscan`, or
2. Use `strict` mode with a pinned host key in the connector configuration.

See the [connector documentation](https://docs.airbyte.com/integrations/destinations/sftp-json) for details.
