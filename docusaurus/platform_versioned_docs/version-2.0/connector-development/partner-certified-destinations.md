# Requirements for Airbyte Partner Connectors: Bulk and Publish Destinations

## Welcome

**Thank you for contributing and committing to maintain your Airbyte destination connector 🥂**

This document outlines the minimum expectations for partner-certified destination.  We will **strongly** recommend that partners use the relevant CDK, but also want to support developers that *need* to develop in a different language.  This document covers concepts implicitly built into our CDKs for this use-case.

## Definitions
**Partner Certified Destination:** A destination which is fully supported by the maintainers of the platform that is being loaded to. These connectors are not guaranteed by Airbyte directly, but instead the maintainers of the connector contribute fixes and improvements to ensure a quality experience for Airbyte users. Partner destinations are noted as such with a special “Partner” badge on the Integrations page, distinguishing them from other community maintained connectors on the Marketplace.


**Bulk Destinations:** A destination which accepts tables and columns as input, files, or otherwise unconstrained content. The majority of bulk destinations are database-like tabular (warehouses, data lakes, databases), but may also include file or blob destinations.  The defining characteristic of bulk destinations is that they accept data in the shape of the source (e.g. tables, columns or content doesn’t change much from the representation of the source).  These destinations can usually hold large amounts of data, and are the fastest to load.

**Publish Destinations:** A publish-type destination, often called a “reverse ETL” destination loads data to an external service or API. These destinations may be “picky”, having specific schema requirements for incoming streams. Common publish-type use cases include: publishing data to a REST API, publishing data to a messaging endpoint (e.g email, push notifications, etc.), and publishing data to an LLM vector store. Specific examples include: Destination-Pinecone, Destination-Vectara, and Destination-Weaviate.  These destinations can usually hold finite amounts of data, and slower to load.

## “Partner-Certified" Listing Requirements:

### Issue Tracking:
Create a public Github repo/project to be shared with Airbyte and it's users.

### Airbyte Communications:
Monitor a Slack channel for communications directly from the Airbyte Support and Development teams.

### SLAs:
Respect a 3 business day first response maximum to customer inquries or bug reports.

### Metrics:
Maintain >=95% first-sync success and >=95% overall sync success on your destination connector. _Note: config_errors are not counted against this metric._

### Platform Updates:
Adhere to a regular update cadence for either the relevant Airbyte-managed CDK, or a commit to updating your connector to meet any new platform requirements at least once every 6 months.

### Connector Updates:
Important bugs are audited and major problems are solved within a reasonable timeframe.

### Security:
Validate that the connector is using HTTPS and secure-only access to customer data.


## Functional Requirements of Certified Destinations:

### Protocol

We won’t call out every requirement of the Airbyte Protocol (link) but below are important requirements that are specific to Destinations and/or specific to Airbyte 1.0 Destinations.

* Destinations must capture state messages from sources, and must emit those state messages to STDOUT only after all preceding records have been durably committed to the destination
  * The Airbyte platform interprets state messages emitted from the destination as a logical checkpoint. Destinations must emit all of the state messages they receive, and only after records have been durably written and/or committed to the destination’s long-term storage.
  * If a destination emits the source’s state message before preceding records are finalized, this is an error.
  * _Note: In general, state handling should always be handled by the respective CDK. Destination authors should not attempt to handle this themselves._

* Destinations must append record counts to the Source’s state message before emitting (New for Airbyte 1.0)
  * For each state record emitted, the destination should attach to the state message the count of records processed and associated with that state message.
  * This should always be handled by the Python or Java CDK. Destination authors should not attempt to handle this themselves.

* State messages should be emitted with no gap longer than 15 minutes
  * Checkpointing requires commit and return state every 15 minutes. When batching records for efficiency, destination should also include logic to finalize batches approximately every 10 minutes, or whatever interval is appropriate to meet the minimum 15 minute checkpoint frequency.
  * This measure reduces the risk of users and improves the efficiency of retries, should an error occur either in the source or destination.

### Idempotence

Syncs should always be re-runnable without negative side effects. For instance, if the table is loaded multiple times, the destination should dedupe records according to the provided primary key information if and when available.

If deduping is disabled, then loads should either fully replace or append  to destination tables - according to the user-provided setting in the configured catalog.

### Exceptions

**Bulk Destinations** should handle metadata and logging of exceptions in a consistent manner.

_Note: Because **Publish Destinations** have little control over table structures, these constraints do not apply to Publish or Reverse-ETL Destinations. This does not apply to vector store destinations, for instance._

* Columns should include all top-level field declarations.
  * Destination tables should have column definitions for each declared top-level property. For instance, if a stream has a “user_id” property, the destination table should contain a “user_id” column.
  * Casing may be normalized (for instance, all-caps or all-lower-case) according to the norms and/or expectations for the destination systems. (For example, Snowflake only works as expected when you normalize to all-caps.)

* Tables should always include the following Airbyte metadata columns: _airbyte_meta, _airbyte_extracted_at, and _airbyte_raw_id
  * These column names should be standard across tabular destinations, including all SQL-type and file-type destinations.

* Bulk Destinations must utilize _airbyte_meta.changes[] to record in-flight fixes or changes
  * This includes logging information on any fields that had to be nullified due to destination capacity restrictions (e.g. data could not fit), and/or problematic input data (e.g. impossible date or out-of-range date).
  * It’s also OK for the destination to make record changes (e.g. property too large to fit) as long as the change doesn’t apply to the PK or cursor, and the change is record in _airbyte_meta.changes[] as well.

* Bulk Destinations must accept new columns arriving from the source. (“Schema Evolution”)
  * Tabular destinations should be consistent in how they handle schema evolutions over the period of a connection’s lifecycle, including gracefully handling expected organic schema evolutions, including the addition of new columns after the initial sync.
  * A new column arriving in the source data should never be a breaking change. Destinations should be able to detect the arrival of a new column and automatically add it to the destination table. (The platform will throttle this somewhat, according to the users’ preference.)

### Configuration Requirements

All destinations are required to adhere to standard configuration practices for connectors. These requirements include, but are not limited to the following:

* The connector `SPEC` output should include RegEx validation rules for configuration parameters. These will be used in the Airbyte Platform UI to pre-validate user inputs, and provide appropriate guidance to users during setup.
* The `CHECK` operation should consider all configuration inputs and produce reasonable error messages for most common configuration errors.
* All customer secrets specified in `SPEC` should be properly annotated with `"airbyte_secret" : true` in the config requirements. This informs the Airbyte Platform that values should not be echoed to the screen during user input, and it ensures that secrets are properly handled as such when storing and retrieving settings in the backend.
* The connector’s manifest must specify `AllowedHosts` - limiting which APIs/IPs this connector can communicate with.

### Data Fidelity and Data Types

**Every attempt should be made to ensure data does not lose fidelity during transit and that syncs do not fail due to data type mapping issues.**

_Note: Publish-type destinations may be excluded from some or all of the below rules, if they are constrained to use predefined types. In these cases, the destination should aim to fail early so the user can reconfigure their source before causing any data corruption or data inconsistencies from partially-loaded datasets._


* Data types should be _at least_ as large as needed to store incoming data.
  * Larger types should be preferred in cases where there is a choice - for instance a choice between INT32 or INT64, the latter should be preferred.


* Floats should be handled with the maximum possible size for floating point numbers
  * Normally this means a `double` precision floating point type.


* Decimals should be handled with the largest-possible precision and scale, generally `DECIMAL(38, 9)`
  * This allows for very-large integers (for example, Active Directory IDs) as well as very precise small numbers - to the 9th decimal place.
  * Floating point storage should _not_ be used for decimals and other numeric values unless they are declared as `float` in the source catalog.


* Destinations should always have a “failsafe” type they can use, in case source type is not known
  * A classic example of this is receiving a column with the type `anyOf(string, object)`. In the case that a good type cannot be chosen, we should fall back to _either_ string types _or_ variable/variant/json types.
  * The failsafe type ensures that data loads will not fail, even when there is a failure to recognize or parse the declared data type.

### Error Handling

Any errors must be logged by the destination using an approved protocol. Silent errors are not permitted, but we bias towards _not_ failing an entire sync when other valid records are able to be written. Only if errors cannot be logged using an approved protocol, then the destination _must fail_ and should raise the error to the attention of the user and the platform.

**Bulk Destinations:** Errors should be recorded along with the record data, in the `_airbyte_meta` column, under the `_airbyte_meta.changes` key.

**Publish Destinations:** In absence of another specific means of communicating to the user that there was an issue, the destination _must fail_ if it is not able to write data to the destination platform. (Additional approved logging protocols may be added in the future for publish-type destinations - for instance, dead letter queues, destination-specific state artifacts, and/or other durable storage medium which could be configured by the user.
