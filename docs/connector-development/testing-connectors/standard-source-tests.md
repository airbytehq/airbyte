# Standard Source Test Suite

Test methods start with `test`. Other methods are internal helpers in the java class implementing the test suite.

## testGetSpec

Verify that a spec operation issued to the connector returns a valid spec.

## testCheckConnection

Verify that a check operation issued to the connector with the input config file returns a success response.

## testDiscover

Verifies when a discover operation is run on the connector using the given config file, a valid catalog is output by the connector.

## testFullRefreshRead

Configuring all streams in the input catalog to full refresh mode, verifies that a read operation produces some RECORD messages.

## testIdenticalFullRefreshes

Configuring all streams in the input catalog to full refresh mode, performs two read operations on all streams which support full refresh syncs. It then verifies that the RECORD messages output from both were identical.

## testIncrementalSyncWithState

This test verifies that all streams in the input catalog which support incremental sync can do so correctly. It does this by running two read operations on the connector's Docker image: the first takes the configured catalog and config provided to this test as input. It then verifies that the sync produced a non-zero number of RECORD and STATE messages. The second read takes the same catalog and config used in the first test, plus the last STATE message output by the first read operation as the input state file. It verifies that no records are produced \(since we read all records in the first sync\). This test is performed only for streams which support incremental. Streams which do not support incremental sync are ignored. If no streams in the input catalog support incremental sync, this test is skipped.

## testEmptyStateIncrementalIdenticalToFullRefresh

If the source does not support incremental sync, this test is skipped. Otherwise, this test runs two syncs: one where all streams provided in the input catalog sync in full refresh mode, and another where all the streams which in the input catalog which support incremental, sync in incremental mode \(streams which don't support incremental sync in full refresh mode\). Then, the test asserts that the two syncs produced the same RECORD messages. Any other type of message is disregarded.

## testEntrypointEnvVar

In order to launch a source on Kubernetes in a pod, we need to be able to wrap the entrypoint. The source connector must specify its entrypoint in the AIRBYTE_ENTRYPOINT variable. This test ensures that the entrypoint environment variable is set.

