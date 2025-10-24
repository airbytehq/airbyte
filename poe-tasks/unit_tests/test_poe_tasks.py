# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from poe_tasks.detect-python-cdk import is_prerelease_version

# Unit tests for is_prerelease_version()
def test_is_prerelease_version():
    """Test cases for is_prerelease_version function."""
    
    # Test standard production versions (should return False)
    assert is_prerelease_version("1.0.0") == False
    assert is_prerelease_version("^1.0.0") == False
    assert is_prerelease_version("~1.0.0") == False
    assert is_prerelease_version(">=1.0.0") == False
    assert is_prerelease_version("<2.0.0") == False
    assert is_prerelease_version("1.2") == False
    assert is_prerelease_version("^6.0.0") == False
    assert is_prerelease_version(">=1.0.0,<2.0.0") == False
    
    # Test prerelease/non-standard versions (should return True)
    assert is_prerelease_version("1.0.0a1") == True
    assert is_prerelease_version("1.0.0b2") == True
    assert is_prerelease_version("1.0.0rc1") == True
    assert is_prerelease_version("1.0.0.dev1") == True
    assert is_prerelease_version("1.0.0-alpha") == True
    assert is_prerelease_version("1.0.0-beta.1") == True
    
    # Test edge cases (should return True)
    assert is_prerelease_version("") == True
    assert is_prerelease_version(None) == True
    assert is_prerelease_version("   ") == True
    assert is_prerelease_version("invalid") == True
    assert is_prerelease_version("git+https://github.com/user/repo") == True
    assert is_prerelease_version("./local/path") == True
    
    # Test whitespace handling (should return False for valid versions)
    assert is_prerelease_version("  1.0.0  ") == False
    assert is_prerelease_version(" ^1.0.0 ") == False

if __name__ == "__main__":
    test_is_prerelease_version()
    print("✅ All tests passed!")
    main()