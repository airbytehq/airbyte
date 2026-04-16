---
sidebar_position: 2
---

# Authenticate

After you [enable a connector](../enable-connector), but before your users can do anything with that connector, they must authenticate with that service. Several options exist to build an authentication flow for your users.

- The simplest method is to use Airbyte's Authentication Module, an out-of-the-box login flow.

- It's possible to build your own flow from scratch, using the Agent Engine API.

- If you subscribe to Airbyte, the Agent Engine manages user credentials for you. If you use agent connectors as open source Python packages and don't subscribe to Airbyte, you must manage user credentials yourself.
