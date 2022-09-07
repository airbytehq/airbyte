# Config Database
* `workspace`
  * Each record represents a logical workspace for an Airbyte user. In the open-source version of the product, only one workspace is allowed.
* `actor_definition`
  * Each record represents a connector that Airbyte supports, e.g. Postgres. This table represents all the connectors that is supported by the current running platform.
  * The `actor_type` column tells us whether the record represents a Source or a Destination.
  * The `spec` column is a JSON blob. The schema of this JSON blob matches the [spec](airbyte-protocol.md#actor-specification) model in the Airbyte Protocol. Because the protocol object is JSON, this has to be a JSON blob.
  * The `release_stage` describes the certification level of the connector (e.g. Alpha, Beta, Generally Available).
  * The `docker_repository` field is the name of the docker image associated with the connector definition. `docker_image_tag` is the tag of the docker image and the version of the connector definition.
  * The `source_type` field is only used for Sources, and represents the category of the connector definition (e.g. API, Database).
  * The `resource_requirements` field sets a default resource requirement for any connector of this type. This overrides the default we set for all connector definitions, and it can be overridden by a connection-specific resource requirement.
  * The `public` boolean column, describes if a connector is available to all workspaces or not. For non, `public` connector definitions, they can be provisioned to a workspace using the `actor_definition_workspace_grant` table. `custom` means that the connector is written by a user of the platform (and not packaged into the Airbyte product).
  * Each record contains additional metadata and display data about a connector (e.g. `name` and `icon`), and we should add additional metadata here over time.
* `actor_definition_workspace_grant`
  * Each record represents provisioning a non `public` connector definition to a workspace.
  * todo (cgardens) - should this table have a `created_at` column?
* `actor`
  * Each record represents a configured connector. e.g. A Postgres connector configured to pull data from my database.
  * The `actor_type` column tells us whether the record represents a Source or a Destination.
  * The `actor_definition_id` column is a foreign key to the connector definition that this record is implementing.
  * The `configuration` column is a JSON blob. The schema of this JSON blob matches the schema specified in the `spec` column in the `connectionSpecification` field of the JSON blob. Keep in mind this schema is specific to each connector (e.g. the schema of Postgres and Salesforce are different), which is why this column has to be a JSON blob.
* `actor_catalog`
  * Each record contains a catalog for an actor. The records in this table are meant to be immutable.
  * The `catalog` column is a JSON blob. The schema of this JSON blob matches the [catalog](airbyte-protocol.md#catalog) model in the Airbyte Protocol. Because the protocol object is JSON, this has to be a JSON blob. The `catalog_hash` column is a 32-bit murmur3 hash ( x86 variant) of the `catalog` field to make comparisons easier.
  * todo (cgardens) - should we remove the `modified_at` column? These records should be immutable.
* `actor_catalog_fetch_event`
  * Each record represents an attempt to fetch the catalog for an actor. The records in this table are meant to be immutable.
  * The `actor_id` column represents the actor that the catalog is being fetched for. The `config_hash` represents a hash (32-bit murmur3 hash - x86 variant) of the `configuration` column of that actor, at the time the attempt to fetch occurred.
  * The `catalog_id` is a foreign key to the `actor_catalog` table. It represents the catalog fetched by this attempt. We use the foreign key, because the catalogs are often large and often multiple fetch events result in retrieving the same catalog. Also understanding how often the same catalog is fetched is interesting from a product analytics point of view.
  * The `actor_version` column represents the `actor_definition` version that was in use when the fetch event happened. This column is needed, because while we can infer the `actor_definition` from the foreign key relationship with the `actor` table, we cannot do the same for the version, as that can change over time.
  * todo (cgardens) - should we remove the `modified_at` column? These records should be immutable.
* `connection`
* `connection_operation`
* `operation`
* `stream_reset`
* `state`
* `workspace_service_account`
* `actor_oauth_parameter`
  * The name of this table is misleading. It refers to parameters to be used for any instance of an `actor_definition` (not an `actor`) within a given workspace. For OAuth, the model is that a user is provisioning access to their data to a third party tool (in this case the Airbyte Platform). Each record represents information (e.g. client id, client secret) for that third party that is getting access. 
  * These parameters can be scoped by workspace. If `workspace_id` is not present, then the scope of the parameters is to the whole deployment of the platform (e.g. all workspaces).
  * The `actor_type` column tells us whether the record represents a Source or a Destination.
  * The `configuration` column is a JSON blob. The schema of this JSON blob matches the schema specified in the `spec` column in the `advanced_auth` field of the JSON blob. Keep in mind this schema is specific to each connector (e.g. the schema of Hubspot and Salesforce are different), which is why this column has to be a JSON blob.

## System Tables
* `airbyte_configs` & `airbyte_configs_migrations` are metadata tables used by Flyway (our database migration tool). They are not used for any application use cases. 
* `secrets`
  * This table is used to store secrets in open-source versions of the platform that have not set some other secrets store. This table allows us to use the same code path for secrets handling regardless of whether an external secrets store is set or not. This table is used by default for the open-source product.

# Jobs Database
* `jobs`
* `attempts`

## System Tables
* `airbyte_jobs_migrations` is metadata table used by Flyway (our database migration tool). It is not used for any application use cases.
* `airbyte_metadata`
