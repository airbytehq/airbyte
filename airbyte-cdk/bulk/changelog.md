**Load CDK**

## Version 0.1.23

* **Changed:** Dataflow CDK fails syncs if there are unflushed states at the end of a sync.

## Version 0.1.22

* **Changed:** Add EntraID support to azure-blob-storage.

## Version 0.1.21

* **Changed:** Adds basic socket support.

## Version 0.1.20

* **Changed:** Fix hard failure edge case in stream initialization for in dataflow cdk lifecycle. 

## Version 0.1.18

* **Changed:** Update load dataflow package accounts for stream completes and dest stats.

## Version 0.1.17

* **Changed:** Run aggregate and flush steps on different dispatchers (default and IO respectively).

## Version 0.1.16

**Load CDK**

* **Changed:** Ensure sequential state emission. Remove flushed state/partition keys.

## Version 0.1.15

**Extract CDK**

* **Changed:** Extract CDK logs DB version during Check for all JDBC databases.

## Version 0.1.14

**Load CDK**

* **Changed:** Add agent.

## Version 0.1.13

**Load CDK**

* **Changed:** Make the resources being used by the dataflow CDK configurable.

## Version 0.1.12

**Load CDK**

* **Changed:** Add teardown to the dataflow pipeline.

## Version 0.1.11

**Load CDK**

* **Changed:** Add finalization to the dataflow pipeline.

## Version 0.1.10

Update the version change check to avoid using deprecated libs.

## Version 0.1.7

Update the log4j to allow us to dynamically set the log level via an env variable

## Version 0.1.6

**Load CDK**

* **Changed:** Add the dataflow pipeline. It is a more comprehensive way to write the ingestion pipeline steps. The new pipeline isn't ready to be use in this version.

## Version 0.1.4

* **Changed:** Extract CDK fixes for CDC in socket mode - state, partitioning and full refresh streams.

## Version 0.1.3

## Version 0.1.2

## Version 0.1.1

## Version 0.1.0

* **Changed:** Adopted Semantic Versioning (SemVer) for the CDK to provide more meaningful version numbers.
* **Action Required:** The CDK version must now be set manually in the `build.gradle` file.
