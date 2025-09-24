## Version 0.1.42

Datflow Load CDK: Fixes hang when one of many parallel pipelines fails. Organizes thread pools. 

## Version 0.1.41

**Extract CDK**

* **Changed:** Prevent a devision by zero error when a table cannot be partitioned.

## Version 0.1.40

Add gradle task to bump CDK version + add changelog entry

## Version 0.1.39

Minor fixes with stream completion logic + proto conversion in Load CDK.

* **Changed:** Minor fixes with stream completion logic + proto conversion

## Version 0.1.38

Adds stats support for "speed" mode to the Load CDK

## Version 0.1.37

load-s3: S3Client forces path-style access, to enable minio compatibility

## Version 0.1.36

Use dedicated dispatcher for parse+aggregate stage for an individual pipeline + cache column name lookup

## Version 0.1.35

Fix input stream wiring for dockerized acceptance tests

## Version 0.1.34

Moved version declaration from build.gradle to version.properties

## Version 0.1.33

Load CDK: Low-code API destination support for dynamically defined discover objects and operations

## Version 0.1.32

Fix input stream wiring for non-dockerized acceptance tests in Load CDK.

## Version 0.1.31

Extract CDK: Pass WhereNode to FromSample node so we can apply filters to the sample query.

## Version 0.1.30

Add Low-code API destination support for statically defined discover operations 

## Version 0.1.29

Load CDK: Use correct field name for generation ID meta column.

## Version 0.1.28

Extract CDK: Protobuf encoding fixes to make various types compatible with load(destination) decoding.

## Version 0.1.27

Allow per-test properties for spec integration test

## Version 0.1.26

Improve load-azure-blob-storage documentation.

## Version 0.1.25

Adds proto support to dataflow. Misc transform package cleanup (developer-facing).

## Version 0.1.24

Adds byte counts to emitted state stats.

## Version 0.1.23

Dataflow CDK fails syncs if there are unflushed states at the end of a sync.

## Version 0.1.22

Add EntraID support to azure-blob-storage.

## Version 0.1.21

Adds basic socket support.

## Version 0.1.20

Fix hard failure edge case in stream initialization for in dataflow cdk lifecycle.

## Version 0.1.18

Update load dataflow package accounts for stream completes and dest stats.

## Version 0.1.17

Run aggregate and flush steps on different dispatchers (default and IO respectively).

## Version 0.1.16

Load CDK: Ensure sequential state emission. Remove flushed state/partition keys.

## Version 0.1.15

Extract CDK logs DB version during Check for all JDBC databases.

## Version 0.1.14

Add agent to Load CDK

## Version 0.1.13

Load CDK: Make the resources being used by the dataflow CDK configurable.

## Version 0.1.12

Load CDK: Add teardown to the dataflow pipeline.

## Version 0.1.11

Add finalization to the dataflow pipeline in Load CDK

## Version 0.1.10

Update the version change check to avoid using deprecated libs.

## Version 0.1.7

Update the log4j to allow us to dynamically set the log level via an env variable

## Version 0.1.6

Load CDK: Add the dataflow pipeline. It is a more comprehensive way to write the ingestion pipeline steps. The new pipeline isn't ready to be use in this version.

## Version 0.1.4

Extract CDK fixes for CDC in socket mode - state, partitioning and full refresh streams.

## Version 0.1.3

## Version 0.1.2

## Version 0.1.1

## Version 0.1.0

Adopted Semantic Versioning (SemVer) for the CDK to provide more meaningful version numbers, requiring the CDK version to be set manually in the build.gradle file.
