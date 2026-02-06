# Credential Deduplication Strategy

## Overview

The migration script implements intelligent deduplication to handle cases where:
1. Multiple GSM secrets have the same credentials but different configs
2. Multiple GSM secrets have different credentials
3. Multiple login credentials exist for the same connector

## How It Works

### 1. Credential Deduplication (By Fingerprint)

**Auth fields are deduplicated** using SHA256 fingerprinting:
- Only the auth field values are hashed (not config fields)
- When duplicate credentials are detected, only the first occurrence is stored in 1Password
- A warning message is displayed identifying the duplicate

**Example:**
```
GSM Secret A: api_key="sk_test_123", account_id="acct_test"
GSM Secret B: api_key="sk_test_123", account_id="acct_prod"  ← Same api_key!
```

**Result:**
```
1Password Item: stripe
├── Section: test-credentials-api-key
│   └── api_key [password] = "sk_test_123"  ← Stored once
└── Section: test-credentials-backup (credentials reused, no new fields)

Warning: Duplicate credentials in variant 'backup' (same as 'api-key')
```

### 2. Config Fields (No Deduplication)

**Config fields are NEVER deduplicated** - all variants are preserved:

**Example:**
```yaml
# defaults.yaml
api-key:
  account_id: "acct_test"
  start_date: "2020-01-01"

backup:
  account_id: "acct_prod"  ← Different config stored
  start_date: "2021-01-01"
```

### 3. Variant Naming

Variants are inferred from GSM secret names:

| Secret Name | Extracted Variant |
|-------------|-------------------|
| `SECRET_SOURCE-STRIPE__CREDS` | `default` (or inferred from fields) |
| `SECRET_SOURCE-STRIPE_BACKUP__CREDS` | `backup` |
| `SECRET_SOURCE-STRIPE_OAUTH__CREDS` | `oauth` |
| `SECRET_SOURCE-STRIPE_TEST-USER-2__CREDS` | `test-user-2` |

### 4. Multiple Login Credentials

When multiple login credentials exist, they are stored in separate sections:

**Example:**
```
GSM Secret 1: username="test1@example.com", password="pass123"
GSM Secret 2: username="test2@example.com", password="pass456"
```

**Result:**
```
1Password Item: service-now
├── Section: login
│   ├── username [text] = "test1@example.com"
│   └── password [password] = "pass123"
├── Section: login-test-user-2
│   ├── username [text] = "test2@example.com"
│   └── password [password] = "pass456"
```

## Use Cases

### Use Case 1: Same API Key, Different Environments

**Scenario:** You use the same test API key for multiple test environments with different configs.

```
SECRET_SOURCE-STRIPE__CREDS: api_key="sk_test_123", account_id="acct_test"
SECRET_SOURCE-STRIPE_BACKUP__CREDS: api_key="sk_test_123", account_id="acct_prod"
```

**Migration Result:**
- ✅ API key stored once in 1Password (deduplication saves space)
- ✅ Both configs available in `defaults.yaml`
- ✅ Warning displayed about duplicate credentials

### Use Case 2: Multiple Auth Methods

**Scenario:** Connector supports both OAuth and API key authentication.

```
SECRET_SOURCE-STRIPE_OAUTH__CREDS: client_id, client_secret, refresh_token
SECRET_SOURCE-STRIPE_API-KEY__CREDS: api_key
```

**Migration Result:**
- ✅ OAuth credentials in `test-credentials-oauth` section
- ✅ API key credentials in `test-credentials-api-key` section
- ✅ Separate configs for each auth method

### Use Case 3: Multiple Test Accounts

**Scenario:** Need multiple login credentials for testing.

```
SECRET_SOURCE-SERVICE-NOW__CREDS: username, password, base_url
SECRET_SOURCE-SERVICE-NOW_TEST-USER-2__CREDS: username, password, base_url
```

**Migration Result:**
- ✅ Separate login sections: `login`, `login-test-user-2`
- ✅ Separate configs for each test account

## Testing

Run the deduplication test suite:

```bash
cd ~/airbyte/migration_scripts
source .venv/bin/activate
python test_deduplication.py
```

## Verification

To see how deduplication will work for your connectors:

```bash
python verify_pilot.py source-stripe
```

Look for:
- ⚠️ Duplicate credential warnings in the output
- "(credentials reused, no new fields)" annotations in the preview
- Separate config sections for each variant in `defaults.yaml`

## Technical Details

### Fingerprint Calculation

```python
def _calculate_auth_fingerprint(self, auth_data: dict) -> str:
    """Calculate fingerprint from auth fields only."""
    sorted_items = sorted(auth_data.items())
    auth_string = json.dumps(sorted_items, sort_keys=True)
    return hashlib.sha256(auth_string.encode()).hexdigest()[:12]
```

- Only auth field values are included in the fingerprint
- Config fields are excluded (allows different configs with same credentials)
- Login fields are handled separately (multiple login sections supported)

### Deduplication Logic

1. **First pass:** Calculate fingerprint for each secret's auth fields
2. **Duplicate detection:** If fingerprint matches an existing variant, skip storing auth
3. **Config storage:** Always store config fields, regardless of duplicate auth
4. **Warning generation:** Track duplicates for user notification
