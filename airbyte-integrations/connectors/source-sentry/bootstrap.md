## Streams

Sentry is a REST API. Connector has the following streams, and all of them support full refresh only.

* [Events](https://docs.sentry.io/api/events/list-a-projects-events/)
* [Issues](https://docs.sentry.io/api/events/list-a-projects-issues/)

And a [ProjectDetail](https://docs.sentry.io/api/projects/retrieve-a-project/) stream is also implemented just for connection checking.

## Authentication

Sentry API offers three types of [authentication methods](https://docs.sentry.io/api/auth/).

* Auth Token - The most common authentication method in Sentry. Connector only supports this method.
* DSN Authentication - Only some API endpoints support this method. Not supported by this connector.
* API Keys - Keys are passed using HTTP Basic auth, and a legacy means of authenticating. They will still be supported but are disabled for new accounts. Not supported by this connector.