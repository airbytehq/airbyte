## Streams

Firestore is a schemaless document database. A firestore database has collections which have documents inside. This connector uses the [Firestore REST API](https://firebase.google.com/docs/firestore/use-rest-api) to discover streams (ie collections).

Since the database is schemaless, this connector does not try to infer a schema from documents. Instead, it puts the whole document into a JSON string.

In order to support incremental streams, this connector requires a cursor field to be set. This cursor field is expected on all documents in a collection, and Firestore requires a [field override](https://firebase.google.com/docs/reference/firestore/indexes#fieldoverrides) to be able to index documents properly and enable requests.

## Authentication

This connector uses Google Identity OAuth 2.0 tokens to authenticate with the REST API, as per the [documentation recommendation](https://firebase.google.com/docs/firestore/use-rest-api#authentication_and_authorization).

Tokens are retrieved by the connector using the python `google.oauth2` library from a service account json key (property: `google_application_credentials`)