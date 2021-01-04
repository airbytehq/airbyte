/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.standardtest.source;

import static io.airbyte.protocol.models.SyncMode.FULL_REFRESH;
import static io.airbyte.protocol.models.SyncMode.INCREMENTAL;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.DefaultCheckConnectionWorker;
import io.airbyte.workers.DefaultDiscoverCatalogWorker;
import io.airbyte.workers.DefaultGetSpecWorker;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessBuilderFactory;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class StandardSourceTest {

  private static final long JOB_ID = 0L;
  private static final int JOB_ATTEMPT = 0;

  private static final Logger LOGGER = LoggerFactory.getLogger(StandardSourceTest.class);

  private TestDestinationEnv testEnv;

  private Path jobRoot;
  protected Path localRoot;
  private ProcessBuilderFactory pbf;

  /**
   * TODO hack: Various Singer integrations use cursor fields inclusively i.e: they output records
   * whose cursor field >= the provided cursor value. This leads to the last record in a sync to
   * always be the first record in the next sync. This is a fine assumption from a product POV since
   * we offer at-least-once delivery. But for simplicity, the incremental test suite currently assumes
   * that the second incremental read should output no records when provided the state from the first
   * sync. This works for many integrations but not some Singer ones, so we hardcode the list of
   * integrations to skip over when performing those tests.
   */
  private Set<String> IMAGES_TO_SKIP_SECOND_INCREMENTAL_READ = Sets.newHashSet(
      "airbyte/source-intercom-singer",
      "airbyte/source-exchangeratesapi-singer",
      "airbyte/source-hubspot-singer",
      "airbyte/source-marketo-singer",
      "airbyte/source-twilio-singer",
      "airbyte/source-salesforce-singer");

  /**
   * Name of the docker image that the tests will run against.
   *
   * @return docker image name
   */
  protected abstract String getImageName();

  /**
   * Specification for integration. Will be passed to integration where appropriate in each test.
   * Should be valid.
   *
   * @return integration-specific configuration
   */
  protected abstract ConnectorSpecification getSpec() throws Exception;

  /**
   * Configuration specific to the integration. Will be passed to integration where appropriate in
   * each test. Should be valid.
   *
   * @return integration-specific configuration
   */
  protected abstract JsonNode getConfig() throws Exception;

  /**
   * The catalog to use to validate the output of read operations. This will be used as follows:
   * <p>
   * Full Refresh syncs will be tested on all the input streams which support it Incremental syncs: -
   * if the stream declares a source-defined cursor, it will be tested with an incremental sync using
   * the default cursor. - if the stream requires a user-defined cursor, it will be tested with the
   * input cursor in both cases, the input {@link #getState()} will be used as the input state.
   *
   * @return
   * @throws Exception
   */
  protected abstract ConfiguredAirbyteCatalog getConfiguredCatalog() throws Exception;

  /**
   * @return a JSON file representing the state file to use when testing incremental syncs
   */
  protected abstract JsonNode getState() throws Exception;

  /**
   * List of regular expressions that should match the output of the test sync.
   *
   * @return the regular expressions to test
   * @throws Exception - thrown when attempting ot access the regexes fails
   */
  protected abstract List<String> getRegexTests() throws Exception;

  /**
   * Function that performs any setup of external resources required for the test. e.g. instantiate a
   * postgres database. This function will be called before EACH test.
   *
   * @param testEnv - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected abstract void setup(TestDestinationEnv testEnv) throws Exception;

  /**
   * Function that performs any clean up of external resources required for the test. e.g. delete a
   * postgres database. This function will be called after EACH test. It MUST remove all data in the
   * destination so that there is no contamination across tests.
   *
   * @param testEnv - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected abstract void tearDown(TestDestinationEnv testEnv) throws Exception;

  @BeforeEach
  public void setUpInternal() throws Exception {
    final Path testDir = Path.of("/tmp/airbyte_tests/");
    Files.createDirectories(testDir);
    final Path workspaceRoot = Files.createTempDirectory(testDir, "test");
    jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"));
    localRoot = Files.createTempDirectory(testDir, "output");
    testEnv = new TestDestinationEnv(localRoot);

    setup(testEnv);

    pbf = new DockerProcessBuilderFactory(
        workspaceRoot,
        workspaceRoot.toString(),
        localRoot.toString(),
        "host");
  }

  @AfterEach
  public void tearDownInternal() throws Exception {
    tearDown(testEnv);
  }

  /**
   * Verify that a spec operation issued to the connector returns a valid spec.
   */
  @Test
  public void testGetSpec() throws Exception {
    final OutputAndStatus<StandardGetSpecOutput> output = runSpec();
    assertTrue(output.getOutput().isPresent(), "Expected spec not to be empty");
    assertEquals(getSpec(), output.getOutput().get().getSpecification(),
        "Expected spec output by integration to be equal to spec provided by test runner");
  }

  /**
   * Verify that a check operation issued to the connector with the input config file returns a
   * success response.
   */
  @Test
  public void testCheckConnection() throws Exception {
    final OutputAndStatus<StandardCheckConnectionOutput> output = runCheck();
    assertTrue(output.getOutput().isPresent(), "Expected check connection to succeed when using provided credentials.");
    assertEquals(Status.SUCCEEDED, output.getOutput().get().getStatus(), "Expected check connection operation to succeed");
  }

  // /**
  // * Verify that when given invalid credentials, that check connection returns a failed response.
  // * Assume that the {@link TestSource#getFailCheckConfig()} is invalid.
  // */
  // @Test
  // public void testCheckConnectionInvalidCredentials() throws Exception {
  // final OutputAndStatus<StandardCheckConnectionOutput> output = runCheck();
  // assertTrue(output.getOutput().isPresent());
  // assertEquals(Status.FAILED, output.getOutput().get().getStatus());
  // }

  /**
   * Verifies when a discover operation is run on the connector using the given config file, a valid
   * catalog is output by the connector.
   */
  @Test
  public void testDiscover() throws Exception {
    final OutputAndStatus<StandardDiscoverCatalogOutput> output = runDiscover();
    assertTrue(output.getOutput().isPresent(), "Expected discover to produce a catalog");
    // the worker validates that it is a valid catalog, so we do not need to validate again (as long as
    // we use the worker, which we will not want to do long term).
    assertNotNull(output.getOutput().get().getCatalog(), "Expected discover to produce a catalog");
  }

  /**
   * Configuring all streams in the input catalog to full refresh mode, verifies that a read operation
   * produces some RECORD messages.
   */
  @Test
  public void testFullRefreshRead() throws Exception {
    final List<AirbyteMessage> allMessages = runRead(withFullRefreshSyncModes(getConfiguredCatalog()));
    final List<AirbyteMessage> recordMessages = allMessages.stream().filter(m -> m.getType() == Type.RECORD).collect(Collectors.toList());
    // the worker validates the message formats, so we just validate the message content
    // We don't need to validate message format as long as we use the worker, which we will not want to
    // do long term.
    assertFalse(recordMessages.isEmpty(), "Expected a full refresh sync to produce records");

    final List<String> regexTests = getRegexTests();
    final List<String> stringMessages = allMessages.stream().map(Jsons::serialize).collect(Collectors.toList());
    LOGGER.info("Running " + regexTests.size() + " regex tests...");
    regexTests.forEach(regex -> {
      LOGGER.info("Looking for [" + regex + "]");
      assertTrue(stringMessages.stream().anyMatch(line -> line.matches(regex)), "Failed to find regex: " + regex);
    });
  }

  /**
   * Configuring all streams in the input catalog to full refresh mode, performs two read operations
   * on all streams which support full refresh syncs. It then verifies that the RECORD messages output
   * from both were identical.
   */
  @Test
  public void testIdenticalFullRefreshes() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = withFullRefreshSyncModes(getConfiguredCatalog());
    final List<AirbyteRecordMessage> recordMessagesFirstRun = filterRecords(runRead(configuredCatalog));
    final List<AirbyteRecordMessage> recordMessagesSecondRun = filterRecords(runRead(configuredCatalog));
    // the worker validates the messages, so we just validate the message, so we do not need to validate
    // again (as long as we use the worker, which we will not want to do long term).
    final String assertionMessage = "Expected two full refresh syncs to produce the same records";
    assertFalse(recordMessagesFirstRun.isEmpty(), assertionMessage);
    assertFalse(recordMessagesSecondRun.isEmpty(), assertionMessage);

    assertSameRecords(recordMessagesFirstRun, recordMessagesSecondRun, assertionMessage);
  }

  /**
   * This test verifies that all streams in the input catalog which support incremental sync can do so
   * correctly. It does this by running two read operations on the connector's Docker image: the first
   * takes the configured catalog and config provided to this test as input. It then verifies that the
   * sync produced a non-zero number of RECORD and STATE messages.
   *
   * The second read takes the same catalog and config used in the first test, plus the last STATE
   * message output by the first read operation as the input state file. It verifies that no records
   * are produced (since we read all records in the first sync).
   *
   * This test is performed only for streams which support incremental. Streams which do not support
   * incremental sync are ignored. If no streams in the input catalog support incremental sync, this
   * test is skipped.
   */
  @Test
  public void testIncrementalSyncWithState() throws Exception {
    if (!sourceSupportsIncremental()) {
      return;
    }

    final ConfiguredAirbyteCatalog configuredCatalog = withSourceDefinedCursors(getConfiguredCatalog());
    // only sync incremental streams
    configuredCatalog.setStreams(
        configuredCatalog.getStreams().stream().filter(s -> s.getSyncMode() == INCREMENTAL).collect(Collectors.toList()));

    final List<AirbyteMessage> airbyteMessages = runRead(configuredCatalog, getState());
    final List<AirbyteRecordMessage> recordMessages = filterRecords(airbyteMessages);
    final List<AirbyteStateMessage> stateMessages = airbyteMessages
        .stream()
        .filter(m -> m.getType() == Type.STATE)
        .map(AirbyteMessage::getState)
        .collect(Collectors.toList());

    assertFalse(recordMessages.isEmpty(), "Expected the first incremental sync to produce records");
    assertFalse(stateMessages.isEmpty(), "Expected incremental sync to produce STATE messages");
    // TODO validate exact records

    if (IMAGES_TO_SKIP_SECOND_INCREMENTAL_READ.contains(getImageName().split(":")[0])) {
      return;
    }

    // when we run incremental sync again there should be no new records. Run a sync with the latest
    // state message and assert no records were emitted.
    final JsonNode latestState = stateMessages.get(stateMessages.size() - 1).getData();
    final List<AirbyteRecordMessage> secondSyncRecords = filterRecords(runRead(configuredCatalog, latestState));
    assertTrue(
        secondSyncRecords.isEmpty(),
        "Expected the second incremental sync to produce no records when given the first sync's output state.");
  }

  /**
   * If the source does not support incremental sync, this test is skipped.
   *
   * Otherwise, this test runs two syncs: one where all streams provided in the input catalog sync in
   * full refresh mode, and another where all the streams which in the input catalog which support
   * incremental, sync in incremental mode (streams which don't support incremental sync in full
   * refresh mode). Then, the test asserts that the two syncs produced the same RECORD messages. Any
   * other type of message is disregarded.
   *
   */
  @Test
  public void testEmptyStateIncrementalIdenticalToFullRefresh() throws Exception {
    if (!sourceSupportsIncremental()) {
      return;
    }

    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
    final ConfiguredAirbyteCatalog fullRefreshCatalog = withFullRefreshSyncModes(configuredCatalog);

    final List<AirbyteRecordMessage> fullRefreshRecords = filterRecords(runRead(fullRefreshCatalog));
    final List<AirbyteRecordMessage> emptyStateRecords = filterRecords(runRead(configuredCatalog, Jsons.jsonNode(new HashMap<>())));
    final String assertionMessage = "Expected a full refresh sync and incremental sync with no input state to produce identical records";
    assertFalse(fullRefreshRecords.isEmpty(), assertionMessage);
    assertFalse(emptyStateRecords.isEmpty(), assertionMessage);
    assertSameRecords(fullRefreshRecords, emptyStateRecords, assertionMessage);
  }

  private List<AirbyteRecordMessage> filterRecords(Collection<AirbyteMessage> messages) {
    return messages.stream()
        .filter(m -> m.getType() == Type.RECORD)
        .map(AirbyteMessage::getRecord)
        .collect(Collectors.toList());
  }

  private ConfiguredAirbyteCatalog withSourceDefinedCursors(ConfiguredAirbyteCatalog catalog) {
    final ConfiguredAirbyteCatalog clone = Jsons.clone(catalog);
    for (ConfiguredAirbyteStream configuredStream : clone.getStreams()) {
      if (configuredStream.getSyncMode() == INCREMENTAL
          && configuredStream.getStream().getSourceDefinedCursor() != null
          && configuredStream.getStream().getSourceDefinedCursor()) {
        configuredStream.setCursorField(configuredStream.getStream().getDefaultCursorField());
      }
    }
    return clone;
  }

  private ConfiguredAirbyteCatalog withFullRefreshSyncModes(ConfiguredAirbyteCatalog catalog) {
    final ConfiguredAirbyteCatalog clone = Jsons.clone(catalog);
    for (ConfiguredAirbyteStream configuredStream : clone.getStreams()) {
      if (configuredStream.getStream().getSupportedSyncModes().contains(FULL_REFRESH)) {
        configuredStream.setSyncMode(FULL_REFRESH);
      }
    }
    return clone;
  }

  private boolean sourceSupportsIncremental() throws Exception {
    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    for (ConfiguredAirbyteStream stream : catalog.getStreams()) {
      if (stream.getStream().getSupportedSyncModes().contains(INCREMENTAL)) {
        return true;
      }
    }
    return false;
  }

  private OutputAndStatus<StandardGetSpecOutput> runSpec() {
    return new DefaultGetSpecWorker(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), pbf))
        .run(new JobGetSpecConfig().withDockerImage(getImageName()), jobRoot);
  }

  private OutputAndStatus<StandardCheckConnectionOutput> runCheck() throws Exception {
    return new DefaultCheckConnectionWorker(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), pbf))
        .run(new StandardCheckConnectionInput().withConnectionConfiguration(getConfig()), jobRoot);
  }

  private OutputAndStatus<StandardDiscoverCatalogOutput> runDiscover() throws Exception {
    return new DefaultDiscoverCatalogWorker(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), pbf))
        .run(new StandardDiscoverCatalogInput().withConnectionConfiguration(getConfig()), jobRoot);
  }

  private List<AirbyteMessage> runRead(ConfiguredAirbyteCatalog configuredCatalog) throws Exception {
    return runRead(configuredCatalog, null);
  }

  // todo (cgardens) - assume no state since we are all full refresh right now.
  private List<AirbyteMessage> runRead(ConfiguredAirbyteCatalog catalog, JsonNode state) throws Exception {
    final StandardTapConfig tapConfig = new StandardTapConfig()
        .withSourceConnectionConfiguration(getConfig())
        .withState(state == null ? null : new State().withState(state))
        .withCatalog(catalog);

    final AirbyteSource source = new DefaultAirbyteSource(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), pbf));
    final List<AirbyteMessage> messages = new ArrayList<>();

    source.start(tapConfig, jobRoot);
    while (!source.isFinished()) {
      source.attemptRead().ifPresent(messages::add);
    }
    source.close();

    return messages;
  }

  private void assertSameRecords(List<AirbyteRecordMessage> expected, List<AirbyteRecordMessage> actual, String message) {
    final List<AirbyteRecordMessage> prunedExpected = expected.stream().map(this::pruneEmittedAt).collect(Collectors.toList());
    final List<AirbyteRecordMessage> prunedActual = actual.stream().map(this::pruneEmittedAt).collect(Collectors.toList());
    assertEquals(prunedExpected.size(), prunedActual.size(), message);
    assertTrue(prunedExpected.containsAll(prunedActual), message);
    assertTrue(prunedActual.containsAll(prunedExpected), message);
  }

  private AirbyteRecordMessage pruneEmittedAt(AirbyteRecordMessage m) {
    return Jsons.clone(m).withEmittedAt(null);
  }

  public static class TestDestinationEnv {

    private final Path localRoot;

    public TestDestinationEnv(Path localRoot) {
      this.localRoot = localRoot;
    }

    public Path getLocalRoot() {
      return localRoot;
    }

  }

}
