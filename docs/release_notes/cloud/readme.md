# Airbyte Cloud release notes

Airbyte Cloud is updated continuously. You always have the latest features and fixes.

## July 14, 2026

Connector Builder

- When you test a stream in the Connector Builder, the test button now checks for configuration errors only in the stream you're testing, along with your global and user input settings. You can now test a stream even when a different stream in the same connector still has errors.

Platform

- If your organization uses single sign-on (SSO), sign-ins are now rejected when your identity provider presents a user whose email domain your organization hasn't verified. This prevents unverified email domains from being used to access your organization.
