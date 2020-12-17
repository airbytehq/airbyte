# Standard Source Test Suite
Test methods start with `test`. Other methods are internal helpers in the java class implementing the test suite.
### getImageName
Name of the docker image that the tests will run against.

### getSpec
Specification for integration. Will be passed to integration where appropriate in each test. Should be valid.

### getConfig
Configuration specific to the integration. Will be passed to integration where appropriate in each test. Should be valid.

### getConfiguredCatalog
The catalog to use to validate the output of read operations. This will be used as follows: Full Refresh syncs will be tested on all the input streams which support it Incremental syncs: - if the stream declares a source-defined cursor, it will be tested with an incremental sync using the default cursor. - if the stream requires a user-defined cursor, it will be tested with the input cursor in both cases, the input getState() will be used as the input state.

### getState
No method description was provided

### getRegexTests
List of regular expressions that should match the output of the test sync.

### setup
Function that performs any setup of external resources required for the test. e.g. instantiate a postgres database. This function will be called before EACH test.

### tearDown
Function that performs any clean up of external resources required for the test. e.g. delete a postgres database. This function will be called after EACH test. It MUST remove all data in the destination so that there is no contamination across tests.

### setUpInternal
No method description was provided

### tearDownInternal
No method description was provided

### testGetSpec
Verify that a spec operation issued to the connector returns a valid spec.

### testCheckConnection
Verify that a check operation issued to the connector with the input config file returns a success response.

### testDiscover
Verifies when a discover operation is run on the connector using the given config file, a valid catalog is output by the connector.

### testFullRefreshRead
Configuring all streams in the input catalog to full refresh mode, verifies that a read operation produces some RECORD messages.

### testIdenticalFullRefreshes
Configuring all streams in the input catalog to full refresh mode, performs two read operations on all streams which support full refresh syncs. It then verifies that the RECORD messages output from both were identical.

### testIncrementalSyncWithState
This test verifies that all streams in the input catalog which support incremental sync can do so correctly. It does this by running two read operations on the connector's Docker image: the first takes the configured catalog and config provided to this test as input. It then verifies that the sync produced a non-zero number of RECORD and STATE messages. The second read takes the same catalog and config used in the first test, plus the last STATE message output by the first read operation as the input state file. It verifies that no records are produced (since we read all records in the first sync). This test is performed only for streams which support incremental. Streams which do not support incremental sync are ignored.

### testEmptyStateIncrementalIdenticalToFullRefresh
If the source does not support incremental sync, this test is skipped. Otherwise, this test runs two syncs: one where all streams provided in the input catalog sync in full refresh mode, and another where all the streams which in the input catalog which support incremental, sync in incremental mode (streams which don't support incremental sync in full refresh mode). Then, the test asserts that the two syncs produced the same RECORD messages. Any other type of message is disregarded.

