# airbyte-oauth

Library for request handling for OAuth Connectors. While Connectors define many OAuth attributes in their spec, the request sequence is executed in the `airbyte-server`. This module contains that logic.

## Key Files
* `OAuthFlowImplementation.java` - interface that a source has to implement in order to do OAuth with Airbyte.
* `OAuthImplementationFactory.java` - catalog of the sources for which we support OAuth.
