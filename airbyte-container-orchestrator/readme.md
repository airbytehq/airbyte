# airbyte-container-orchestrator

This module contains logic to handle launching connector containers. It is called from the temporal workflows in `airbyte-workers`. It is called from the worker and spins up in a separate pod so that sync workflows can be isolated from each other.

## Entrypoint
* `ContainerOrchestratorApp.java`
