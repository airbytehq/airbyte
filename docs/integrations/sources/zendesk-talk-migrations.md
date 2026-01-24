# Zendesk Talk Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 2.0.0

This version adds OAuth2.0 with refresh token support. Users who authenticate via OAuth must re-authenticate to use the new flow with rotating refresh tokens.

### What changed

Zendesk introduced the OAuth refresh token grant type as part of their transition to expiring access tokens. The previous OAuth implementation used non-expiring access tokens, which Zendesk is deprecating. The new OAuth2.0 flow uses rotating refresh tokens, where each token refresh returns a new refresh token and invalidates the previous one.

The connector now offers three authentication options:

- **OAuth2.0**: The new recommended method with refresh token support. This option automatically refreshes access tokens using Zendesk's rotating refresh token flow.
- **API Token**: Uses a Zendesk API token with email authentication. This method is unaffected by this change.
- **OAuth2.0 (Legacy)**: The previous OAuth implementation using non-expiring access tokens. This option remains available for backward compatibility but will eventually be deprecated by Zendesk.

For more information about Zendesk's OAuth changes, see [Zendesk's OAuth grant-type tokens documentation](https://developer.zendesk.com/api-reference/ticketing/oauth/grant_type_tokens/).

### Who is affected

This change affects users who authenticate using OAuth2.0. Users who authenticate using API tokens are not affected.

### Migration steps

1. Go to your Zendesk Talk connection settings in Airbyte.
2. If you are using OAuth authentication, you will need to re-authenticate.
3. Select **OAuth2.0** as the authentication method.
4. Complete the OAuth flow to authorize the connector.

After re-authenticating, the connector will automatically handle token refresh using the new rotating refresh token flow.

### Connector upgrade guide

<MigrationGuide />

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte. As part of our commitment to delivering exceptional service, we are transitioning source zendesk-talk from the Python Connector Development Kit (CDK) to our innovative low-code framework. This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog. However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

We’ve evolved and standardized how state is managed for incremental streams that are nested within a parent stream. This change impacts how individual states are tracked and stored for each partition, using a more structured approach to ensure the most granular and flexible state management. This change will affect the `calls` and `call_legs` streams.

To gracefully handle these changes for your existing connections, we highly recommend resetting your data before resuming your data syncs with the new version.

## Connector upgrade guide

<MigrationGuide />
