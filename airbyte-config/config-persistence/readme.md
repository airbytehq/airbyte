# airbyte-config:config-persistence

This module contains the logic for accessing the config database. This database is primarily used by the `airbyte-server` but is also accessed from `airbyte-workers`. It contains all configuration information for Airbyte.

## Key files
* `ConfigPersistence.java` is the interface over "low-level" access to the db. The most commonly used implementation of it is `DatabaseConfigPersistence.java`.
* `ConfigRepository.java` is what is most used for accessing the databases. The `ConfigPersistence` iface was hard to work with. `ConfigRepository` builds on top of it and houses any databases queries to keep them from proliferating throughout the codebase.
