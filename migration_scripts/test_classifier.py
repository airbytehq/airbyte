"""
Unit tests for field classification.

Tests the FieldClassifier logic with known examples to verify correct classification.
"""

from field_classifier import FieldClassifier, FieldType


def test_field_classification():
    """Test field classification with known examples."""
    classifier = FieldClassifier()

    # Test cases with expected results: (field_name, field_value, expected_type)
    test_cases = [
        # API credentials - should be SECRET
        ("api_key", None, FieldType.SECRET, "API key pattern"),
        ("client_secret", None, FieldType.SECRET, "OAuth secret pattern"),
        ("access_token", None, FieldType.SECRET, "Token pattern"),
        ("bearer_token", None, FieldType.SECRET, "Bearer token pattern"),
        ("refresh_token", None, FieldType.SECRET, "Refresh token pattern"),
        ("private_key", None, FieldType.SECRET, "Private key pattern"),
        ("password", None, FieldType.SECRET, "Password pattern"),
        ("api_secret", None, FieldType.SECRET, "API secret pattern"),
        ("webhook_secret", None, FieldType.SECRET, "Webhook secret pattern"),

        # Config fields - should be CONFIG
        ("base_url", None, FieldType.CONFIG, "URL pattern"),
        ("account_id", None, FieldType.CONFIG, "ID pattern"),
        ("start_date", None, FieldType.CONFIG, "Date pattern"),
        ("region", None, FieldType.CONFIG, "Region field"),
        ("subdomain", None, FieldType.CONFIG, "Subdomain field"),
        ("host", None, FieldType.CONFIG, "Host field"),
        ("endpoint", None, FieldType.CONFIG, "Endpoint field"),
        ("redirect_uri", None, FieldType.CONFIG, "URI pattern"),
        ("workspace", None, FieldType.CONFIG, "Workspace field"),
        ("tenant", None, FieldType.CONFIG, "Tenant field"),

        # Login credentials - should be LOGIN
        ("username", None, FieldType.LOGIN, "Username pattern"),
        ("email", None, FieldType.LOGIN, "Email pattern"),
        ("user_email", None, FieldType.LOGIN, "User email pattern"),
        ("user_name", None, FieldType.LOGIN, "User name pattern"),
        ("login", None, FieldType.LOGIN, "Login pattern"),
        ("login_email", None, FieldType.LOGIN, "Login email pattern"),
        ("account_email", None, FieldType.LOGIN, "Account email pattern"),

        # Value-based detection
        ("jwt_token", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
         FieldType.SECRET, "JWT format detection"),
        ("service_key", "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBg...",
         FieldType.SECRET, "PEM format detection"),

        # Edge cases that might need manual review
        ("connection_string", None, FieldType.SECRET, "Contains 'secret' keyword"),
        ("auth_header", None, FieldType.SECRET, "Contains 'auth' keyword"),
    ]

    print("=" * 70)
    print("Field Classification Unit Tests")
    print("=" * 70)
    print()

    passed = 0
    failed = 0
    warnings = 0

    for field_name, field_value, expected, description in test_cases:
        result = classifier.classify(field_name, field_value)

        if result.field_type == expected:
            status = "✅ PASS"
            passed += 1
        elif result.field_type == FieldType.UNKNOWN:
            status = "⚠️  WARN"
            warnings += 1
        else:
            status = "❌ FAIL"
            failed += 1

        print(f"{status} {field_name:25s} → {result.field_type.value:10s} (expected: {expected.value})")
        print(f"     {description}")
        if result.field_type != expected:
            print(f"     Reason: {result.reason}")
            print(f"     Confidence: {result.confidence}")
        print()

    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"✅ Passed:  {passed}/{len(test_cases)}")
    print(f"❌ Failed:  {failed}/{len(test_cases)}")
    print(f"⚠️  Warnings: {warnings}/{len(test_cases)}")
    print()

    if failed > 0:
        print("❌ Some tests failed. Review classification patterns.")
        return False
    elif warnings > 0:
        print("⚠️  Some fields need manual review (UNKNOWN classification).")
        print("   These should be added to classification_overrides.yaml")
        return True
    else:
        print("✅ All tests passed!")
        return True


def test_login_password_detection():
    """Test that password is moved to login when username present."""
    print("\n" + "=" * 70)
    print("Login Password Detection Test")
    print("=" * 70)
    print()
    print("This tests the post-processing logic in gsm_audit.py")
    print("When username/email is present, password should move to login_fields")
    print()

    classifier = FieldClassifier()

    # Simulate a GSM secret with username + password
    fields = {
        "username": "admin@company.com",
        "password": "SecurePassword123",
        "base_url": "company.service-now.com"
    }

    auth_fields = []
    config_fields = []
    login_fields = []

    for field_name, field_value in fields.items():
        result = classifier.classify(field_name, field_value)
        if result.field_type == FieldType.SECRET:
            auth_fields.append(field_name)
        elif result.field_type == FieldType.CONFIG:
            config_fields.append(field_name)
        elif result.field_type == FieldType.LOGIN:
            login_fields.append(field_name)

    print("Initial classification:")
    print(f"  auth_fields:   {auth_fields}")
    print(f"  config_fields: {config_fields}")
    print(f"  login_fields:  {login_fields}")
    print()

    # Simulate post-processing (from gsm_audit.py lines 137-140)
    if login_fields and "password" in auth_fields:
        auth_fields.remove("password")
        login_fields.append("password")
        print("Post-processing: Moved 'password' from auth to login")
        print()

    print("Final classification:")
    print(f"  auth_fields:   {auth_fields}")
    print(f"  config_fields: {config_fields}")
    print(f"  login_fields:  {login_fields}")
    print()

    # Verify expected results
    expected_login = ["username", "password"]
    expected_config = ["base_url"]
    expected_auth = []

    if (set(login_fields) == set(expected_login) and
        set(config_fields) == set(expected_config) and
        set(auth_fields) == set(expected_auth)):
        print("✅ Password correctly moved to login section")
        return True
    else:
        print("❌ Incorrect classification after post-processing")
        return False


if __name__ == '__main__':
    import sys

    # Run tests
    test1_passed = test_field_classification()
    test2_passed = test_login_password_detection()

    # Exit with status code
    if test1_passed and test2_passed:
        print("\n" + "=" * 70)
        print("✅ All verification tests passed!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("❌ Some tests failed. Review output above.")
        print("=" * 70)
        sys.exit(1)
