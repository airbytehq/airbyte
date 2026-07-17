# Airbyte Cloud release notes

Airbyte Cloud is updated continuously. You always have the latest features and fixes.

## July 17, 2026

Connections

- When you connect a source that authenticates through OAuth and the authorization is denied or fails, Airbyte no longer saves an invalid credential. The error is now surfaced so you can correct the problem and try again.

Platform

- If you're invited to an organization but don't yet belong to one, the app now loads correctly so you can view and accept your invitation. Previously these screens could fail to load when your account had no current organization.

## July 14, 2026

Connector Builder

- When you test a stream in the Connector Builder, the test button now checks for configuration errors only in the stream you're testing, along with your global and user input settings. You can now test a stream even when a different stream in the same connector still has errors.

Platform

- If your organization uses single sign-on (SSO), sign-ins are now rejected when your identity provider presents a user whose email domain your organization hasn't verified. This prevents unverified email domains from being used to access your organization.
