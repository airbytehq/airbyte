# Airbyte Databases Data Catalog

## Config Database
* `workspace`
  * Each record represents a logical workspace for an Airbyte user. In the open-source version of the product, only one workspace is allowed.
* `actor_definition`
  * Each record represents a connector that Airbyte supports, e.g. Postgres. This table represents all the connectors that is supported by the current running platform.
  * The `actor_type` column tells us whether the record represents a Source or a Destination.
  * The `spec` column is a JSON blob. The schema of this JSON blob matches the [spec](airbyte-protocol.md#actor-specification) model in the Airbyte Protocol. Because the protocol object is JSON, this has to be a JSON blob.
  * The `release_stage` describes the certification level of the connector (e.g. Alpha, Beta, Generally Available).
  * The `docker_repository` field is the name of the docker image associated with the connector definition. `docker_image_tag` is the tag of the docker image and the version of the connector definition.
  * The `source_type` field is only used for Sources, and represents the category of the connector definition (e.g. API, Database).
  * The `resource_requirements` field sets a default resource requirement for any connector of this type. This overrides the default we set for all connector definitions, and it can be overridden by a connection-specific resource requirement. The column is a JSON blob with the schema defined in [ActorDefinitionResourceRequirements.yaml](https://github.com/airbytehq/airbyte/blob/master/airbyte-config-oss/config-models-oss/src/main/resources/types/ActorDefinitionResourceRequirements.yaml)
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
  * Each record in this table configures a connection (`source_id`, `destination_id`, and relevant configuration).
  * The `resource_requirements` field sets a default resource requirement for the connection. This overrides the default we set for all connector definitions and the default set for the connector definitions. The column is a JSON blob with the schema defined in [ResourceRequirements.yaml](https://github.com/airbytehq/airbyte/blob/master/airbyte-config-oss/config-models-oss/src/main/resources/types/ResourceRequirements.yaml).
  * The `source_catalog_id` column is a foreign key that refers to `id` column in `actor_catalog` table and represents the catalog that was used to configure the connection. This should not be confused with the `catalog` column which contains the [ConfiguredCatalog](airbyte-protocol.md#catalog) for the connection.
  * The `schedule_type` column defines what type of schedule is being used. If the `type` is manual, then `schedule_data` will be null. Otherwise, `schedule_data` column is a JSON blob with the schema of [StandardSync#scheduleData](https://github.com/airbytehq/airbyte/blob/master/airbyte-config-oss/config-models-oss/src/main/resources/types/StandardSync.yaml#L74) that defines the actual schedule. The columns `manual` and `schedule` are deprecated and should be ignored (they will be dropped soon).
  * The `namespace_type` column configures whether the namespace for the connection should use that defined by the source, the destination, or a user-defined format (`custom`). If `custom` the `namespace_format` column defines the string that will be used as the namespace.
  * The `status` column describes the activity level of the connector: `active` - current schedule is respected, `inactive` - current schedule is ignored (the connection does not run) but it could be switched back to active, and `deprecated` - the connection is permanently off (cannot be moved to active or inactive).
* `state`
  * The `state` table represents the current (last) state for a connection. For a connection with `stream` state, there will be a record per stream. For a connection with `global` state, there will be a record per stream and an additional record to store the shared (global) state. For a connection with `legacy` state, there will be one record per connection.
  * In the `stream` and `global` state cases, the `stream_name` and `namespace` columns contains the name of the stream whose state is represented by that record. For the shared state in global `stream_name` and `namespace` will be null.
  * The `state` column contains the state JSON blob. Depending on the type of the connection, the schema of the blob will be different.
    * `stream` - for this type, this column is a JSON blob that is a blackbox to the platform and known only to the connector that generated it.
    * `global` - for this type, this column is a JSON blob that is a blackbox to the platform and known only to the connector that generated it. This is true for both the states for each stream and the shared state.
    * `legacy` - for this type, this column is a JSON blob with a top-level key called `state`. Within that `state` is a blackbox to the platform and known only to the connector that generated it.
  * The `type` column describes the type of the state of the row. type can be `STREAM`, `GLOBAL` or `LEGACY`.
  * The connection_id is a foreign key to the connection for which we are tracking state.
* `stream_reset`
  * Each record in this table represents a stream in a connection that is enqueued to be reset or is currently being reset. It can be thought of as a queue. Once the stream is reset, the record is removed from the table.
* `operation`
  * The `operation` table transformations for a connection beyond the raw output produced by the destination. The two options are: `normalization`, which outputs Airbyte's basic normalization. The second is `dbt`, which allows a user to configure their own custom dbt transformation. A connection can have multiple operations (e.g. it can do `normalization` and `dbt`).
  * If the `operation` is `dbt`, then the `operator_dbt` column will be populated with a JSON blob with the schema from [OperatorDbt](https://github.com/airbytehq/airbyte/blob/master/airbyte-config-oss/config-models-oss/src/main/resources/types/OperatorDbt.yaml).
  * If the `operation` is `normalization`, then the `operator_dbt` column will be populated with a JSON blob with the scehma from [OperatorNormalization](https://github.com/airbytehq/airbyte/blob/master/airbyte-config-oss/config-models-oss/src/main/resources/types/OperatorNormalization.yaml).
  * Operations are scoped by workspace, using the `workspace_id` column.
* `connection_operation`
  * This table joins the `operation` table to the `connection` for which it is configured. 
* `workspace_service_account`
  * This table is a WIP for an unfinished feature.
* `actor_oauth_parameter`
  * The name of this table is misleading. It refers to parameters to be used for any instance of an `actor_definition` (not an `actor`) within a given workspace. For OAuth, the model is that a user is provisioning access to their data to a third party tool (in this case the Airbyte Platform). Each record represents information (e.g. client id, client secret) for that third party that is getting access. 
  * These parameters can be scoped by workspace. If `workspace_id` is not present, then the scope of the parameters is to the whole deployment of the platform (e.g. all workspaces).
  * The `actor_type` column tells us whether the record represents a Source or a Destination.
  * The `configuration` column is a JSON blob. The schema of this JSON blob matches the schema specified in the `spec` column in the `advanced_auth` field of the JSON blob. Keep in mind this schema is specific to each connector (e.g. the schema of Hubspot and Salesforce are different), which is why this column has to be a JSON blob.
* `secrets`
  * This table is used to store secrets in open-source versions of the platform that have not set some other secrets store. This table allows us to use the same code path for secrets handling regardless of whether an external secrets store is set or not. This table is used by default for the open-source product.
* `airbyte_configs_migrations` is metadata table used by Flyway (our database migration tool). It is not used for any application use cases.
* `airbyte_configs`
  * Legacy table for config storage. Should be dropped.

## Jobs Database
* `jobs`
  * Each record in this table represents a job.
  * The `config_type` column captures the type of job. We only make jobs for `sync` and `reset` (we do not use them for `spec`, `check`, `discover`).
  * A job represents an attempt to use a connector (or a pair of connectors). The goal of this model is to capture the input of that run. A job can have multiple attempts (see the `attempts` table). The guarantee across all attempts is that the input into each attempt will be the same.
  * That input is captured in the `config` column. This column is a JSON Blob with the schema of a [JobConfig](https://github.com/airbytehq/airbyte/blob/master/airbyte-config-oss/config-models-oss/src/main/resources/types/JobConfig.yaml). Only `sync` and `resetConnection` are ever used in that model.
    * The other top-level fields are vestigial from when `spec`, `check`, `discover` were used in this model (we will eventually remove them).
  * The `scope` column contains the `connection_id` for the relevant connection of the job.
    * Context: It is called `scope` and not `connection_id`, because, this table was originally used for `spec`, `check`, and `discover`, and in those cases the `scope` referred to the relevant actor or actor definition. At this point the scope is always a `connection_id`.
  * The `status` column contains the job status. The lifecycle of a job is explained in detail in the [Jobs & Workers documentation](jobs.md#job-state-machine).
* `attempts`
  * Each record in this table represents an attempt.
  * Each attempt belongs to a job--this is captured by the `job_id` column. All attempts for a job will run on the same input.
  * The `id` column is a unique id across all attempts while the `attempt_number` is an ascending number of the attempts for a job.
  * The output of each attempt, however, can be different. The `output` column is a JSON blob with the schema of a [JobOutput](ahttps://github.com/airbytehq/airbyte/blob/master/airbyte-config-oss/config-models-oss/src/main/resources/types/StandardSyncOutput.yaml). Only `sync` is used in that model. Reset jobs will also use the `sync` field, because under the hood `reset` jobs end up just doing a `sync` with special inputs. This object contains all the output info for a sync including stats on how much data was moved.
    * The other top-level fields are vestigial from when `spec`, `check`, `discover` were used in this model (we will eventually remove them).
  * The `status` column contains the attempt status. The lifecycle of a job / attempt is explained in detail in the [Jobs & Workers documentation](jobs.md#job-state-machine).
  * If the attempt fails, the `failure_summary` column will be populated. The column is a JSON blob with the schema of [AttemptFailureReason](https://github.com/airbytehq/airbyte/blob/master/airbyte-config-oss/config-models-oss/src/main/resources/types/AttemptFailureSummary.yaml).
  * The `log_path` column captures where logs for the attempt will be written.
  * `created_at`, `started_at`, and `ended_at` track the run time.
  * The `temporal_workflow_id` column keeps track of what temporal execution is associated with the attempt.
* `airbyte_metadata`
  * This table is a key-value store for various metadata about the platform. It is used to track information about what version the platform is currently on as well as tracking the upgrade history.
  * Logically it does not make a lot of sense that it is in the jobs db. It would make sense if it were either in its own dbs or in the config dbs.
  * The only two columns are `key` and `value`. It is truly just a key-value store.
* `airbyte_jobs_migrations` is metadata table used by Flyway (our database migration tool). It is not used for any application use cases.
