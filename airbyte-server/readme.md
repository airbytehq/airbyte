# airbyte-server

This module contains the actual app that runs the Airbyte Configuration API. The main method can be found in `ServerApp.java`.

The external API interface that it implements is declared in `airbyte-api`. The class that actually implements that interface is called `ConfigurationApi`. You will notice that class is very large, because generates a method for every endpoint. To keep it manageable, that class just delegates all requests to more tightly-scoped, resource-based handlers. For example, the `workspace/get` endpoint is present in `ConfigurationApi`, but all it does it delegate the call to the `WorkspaceHandler` which contains all Workspace-specific logic. Unit tests for the server happen at the Handler-level, not for the `ConfigurationApi`.
