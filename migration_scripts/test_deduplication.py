"""
Test deduplication logic with concrete examples.

This script demonstrates how the deduplication works:
1. Same credentials, different configs → Deduplicate auth, keep all configs
2. Different credentials → Keep all auth and config separately
3. Multiple login credentials → Separate login sections
"""

from gsm_to_1password import OnePasswordMigrator


def test_same_creds_different_configs():
    """Test: Same API key, different config values."""
    print("\n" + "="*70)
    print("Test 1: Same Credentials, Different Configs")
    print("="*70)

    # Simulate GSM secrets with same api_key but different configs
    gsm_secrets = [
        {
            "secret_name": "SECRET_SOURCE-STRIPE__CREDS",
            "raw_config": {
                "api_key": "sk_test_123",
                "account_id": "acct_test",
                "start_date": "2020-01-01"
            },
            "auth_fields": ["api_key"],
            "config_fields": ["account_id", "start_date"],
            "login_fields": [],
            "fingerprint": "abc123"
        },
        {
            "secret_name": "SECRET_SOURCE-STRIPE_BACKUP__CREDS",
            "raw_config": {
                "api_key": "sk_test_123",  # Same credential
                "account_id": "acct_prod",  # Different config
                "start_date": "2021-01-01"
            },
            "auth_fields": ["api_key"],
            "config_fields": ["account_id", "start_date"],
            "login_fields": [],
            "fingerprint": "abc123"  # Same fingerprint
        }
    ]

    migrator = OnePasswordMigrator(dry_run=True)
    preview = migrator.generate_preview("source-stripe", gsm_secrets)
    print(preview)

    print("\nExpected behavior:")
    print("  ✓ api_key stored once (in 'default' section)")
    print("  ✓ No auth fields in 'backup' section (duplicate)")
    print("  ✓ Config stored separately for both 'default' and 'backup'")


def test_different_creds():
    """Test: Different API keys → Keep both."""
    print("\n" + "="*70)
    print("Test 2: Different Credentials")
    print("="*70)

    gsm_secrets = [
        {
            "secret_name": "SECRET_SOURCE-STRIPE__CREDS",
            "raw_config": {
                "api_key": "sk_test_123",
                "account_id": "acct_test"
            },
            "auth_fields": ["api_key"],
            "config_fields": ["account_id"],
            "login_fields": [],
            "fingerprint": "abc123"
        },
        {
            "secret_name": "SECRET_SOURCE-STRIPE_BACKUP__CREDS",
            "raw_config": {
                "api_key": "sk_test_789",  # Different credential
                "account_id": "acct_prod"
            },
            "auth_fields": ["api_key"],
            "config_fields": ["account_id"],
            "login_fields": [],
            "fingerprint": "def456"  # Different fingerprint
        }
    ]

    migrator = OnePasswordMigrator(dry_run=True)
    preview = migrator.generate_preview("source-stripe", gsm_secrets)
    print(preview)

    print("\nExpected behavior:")
    print("  ✓ api_key stored in 'default' section")
    print("  ✓ api_key stored in 'backup' section (different value)")
    print("  ✓ Config stored separately for both variants")


def test_multiple_login_creds():
    """Test: Multiple login credentials → Separate sections."""
    print("\n" + "="*70)
    print("Test 3: Multiple Login Credentials")
    print("="*70)

    gsm_secrets = [
        {
            "secret_name": "SECRET_SOURCE-SERVICE-NOW__CREDS",
            "raw_config": {
                "username": "test1@example.com",
                "password": "pass123",
                "base_url": "https://test1.service-now.com"
            },
            "auth_fields": [],
            "config_fields": ["base_url"],
            "login_fields": ["username", "password"],
            "fingerprint": "login1"
        },
        {
            "secret_name": "SECRET_SOURCE-SERVICE-NOW_TEST-USER-2__CREDS",
            "raw_config": {
                "username": "test2@example.com",
                "password": "pass456",
                "base_url": "https://test2.service-now.com"
            },
            "auth_fields": [],
            "config_fields": ["base_url"],
            "login_fields": ["username", "password"],
            "fingerprint": "login2"
        }
    ]

    migrator = OnePasswordMigrator(dry_run=True)
    preview = migrator.generate_preview("source-service-now", gsm_secrets)
    print(preview)

    print("\nExpected behavior:")
    print("  ✓ 'login' section for default credentials")
    print("  ✓ 'login-test-user-2' section for second set")
    print("  ✓ Config stored separately for both variants")


def test_oauth_variants():
    """Test: OAuth and API key variants."""
    print("\n" + "="*70)
    print("Test 4: Multiple Auth Variants (OAuth + API Key)")
    print("="*70)

    gsm_secrets = [
        {
            "secret_name": "SECRET_SOURCE-STRIPE_OAUTH__CREDS",
            "raw_config": {
                "client_id": "ca_ABC123",
                "client_secret": "sk_test_xyz",
                "refresh_token": "rt_789",
                "account_id": "acct_oauth"
            },
            "auth_fields": ["client_id", "client_secret", "refresh_token"],
            "config_fields": ["account_id"],
            "login_fields": [],
            "fingerprint": "oauth1"
        },
        {
            "secret_name": "SECRET_SOURCE-STRIPE_API-KEY__CREDS",
            "raw_config": {
                "api_key": "sk_test_456",
                "account_id": "acct_api"
            },
            "auth_fields": ["api_key"],
            "config_fields": ["account_id"],
            "login_fields": [],
            "fingerprint": "api1"
        }
    ]

    migrator = OnePasswordMigrator(dry_run=True)
    preview = migrator.generate_preview("source-stripe", gsm_secrets)
    print(preview)

    print("\nExpected behavior:")
    print("  ✓ 'test-credentials-oauth' section with 3 auth fields")
    print("  ✓ 'test-credentials-api-key' section with 1 auth field")
    print("  ✓ Config stored separately for both variants")


if __name__ == "__main__":
    test_same_creds_different_configs()
    test_different_creds()
    test_multiple_login_creds()
    test_oauth_variants()

    print("\n" + "="*70)
    print("All deduplication tests completed!")
    print("="*70)
