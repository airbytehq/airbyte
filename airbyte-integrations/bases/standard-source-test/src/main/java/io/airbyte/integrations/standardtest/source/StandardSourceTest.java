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
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.config.StandardSync.SyncMode;
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
import java.util.UUID;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class StandardSourceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(StandardSourceTest.class);

  private TestDestinationEnv testEnv;

  private Path jobRoot;
  protected Path localRoot;
  private ProcessBuilderFactory pbf;

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
    Path testDir = Path.of("/tmp/airbyte_tests/");
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
   * Verify that when the integrations returns a valid spec.
   */
  @Test
  public void testGetSpec() throws Exception {
    final OutputAndStatus<StandardGetSpecOutput> output = runSpec();
    assertTrue(output.getOutput().isPresent());
    assertEquals(getSpec(), output.getOutput().get().getSpecification());
  }

  /**
   * Verify that when given valid credentials, that check connection returns a success response.
   * Assume that the {@link StandardSourceTest#getConfig()} is valid.
   */
  @Test
  public void testCheckConnection() throws Exception {
    final OutputAndStatus<StandardCheckConnectionOutput> output = runCheck();
    assertTrue(output.getOutput().isPresent());
    assertEquals(Status.SUCCEEDED, output.getOutput().get().getStatus());
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
   * Verify that when given valid credentials, that discover returns a valid catalog. Assume that the
   * {@link StandardSourceTest#getConfig()} is valid.
   */
  @Test
  public void testDiscover() throws Exception {
    final OutputAndStatus<StandardDiscoverCatalogOutput> output = runDiscover();
    assertTrue(output.getOutput().isPresent());
    // the worker validates that it is a valid catalog, so we do not need to validate again (as long as
    // we use the worker, which we will not want to do long term).
    assertNotNull(output.getOutput().get().getCatalog());
  }

  /**
   * Verify that the integration successfully writes records. Tests a wide variety of messages and
   * schemas (aspirationally, anyway).
   */
  @Test
  public void testFullRefreshRead() throws Exception {
    final List<AirbyteMessage> allMessages = runRead(withFullRefreshSyncModes(getConfiguredCatalog()));
    final List<AirbyteMessage> recordMessages = allMessages.stream().filter(m -> m.getType() == Type.RECORD).collect(Collectors.toList());
    // the worker validates the message formats, so we just validate the message content
    // We don't need to validate message format as long as we use the worker, which we will not want to
    // do long term.
    assertFalse(recordMessages.isEmpty());

    final List<String> regexTests = getRegexTests();
    final List<String> stringMessages = allMessages.stream().map(Jsons::serialize).collect(Collectors.toList());
    LOGGER.info("Running " + regexTests.size() + " regex tests...");
    regexTests.forEach(regex -> {
      LOGGER.info("Looking for [" + regex + "]");
      assertTrue(stringMessages.stream().anyMatch(line -> line.matches(regex)), "Failed to find regex: " + regex);
    });
  }

  @Test
  public void testIdenticalFullRefreshes() throws Exception {
    ConfiguredAirbyteCatalog configuredCatalog = withFullRefreshSyncModes(getConfiguredCatalog());
    final List<AirbyteRecordMessage> recordMessagesFirstRun = filterRecords(runRead(configuredCatalog));
    final List<AirbyteRecordMessage> recordMessagesSecondRun = filterRecords(runRead(configuredCatalog));
    // the worker validates the messages, so we just validate the message, so we do not need to validate
    // again (as long as we use the worker, which we will not want to do long term).
    assertFalse(recordMessagesFirstRun.isEmpty());
    assertFalse(recordMessagesSecondRun.isEmpty());

    assertSameRecords(recordMessagesFirstRun, recordMessagesSecondRun);
  }

  /**
   * Verify that the source is able to read data incrementally with a given input state.
   */
  @Test
  public void testIncrementalSyncWithState() throws Exception {
    if (!sourceSupportsIncremental()) {
      return;
    }

    ConfiguredAirbyteCatalog configuredAirbyteCatalog = withSourceDefinedCursors(getConfiguredCatalog());
    List<AirbyteMessage> airbyteMessages = runRead(configuredAirbyteCatalog, getState());
    List<AirbyteRecordMessage> recordMessages = filterRecords(airbyteMessages);
    List<AirbyteStateMessage> stateMessages = airbyteMessages
        .stream()
        .filter(m -> m.getType() == Type.STATE)
        .map(AirbyteMessage::getState)
        .collect(Collectors.toList());

    assertFalse(recordMessages.isEmpty());
    assertFalse(stateMessages.isEmpty());
    // TODO validate exact records

    // when we run incremental sync again there should be no new records. Run a sync with the latest
    // state message and assert no records were emitted.
    JsonNode latestState = stateMessages.get(stateMessages.size() - 1).getData();
    List<AirbyteRecordMessage> secondSyncRecords = filterRecords(runRead(configuredAirbyteCatalog, latestState));
    assertTrue(secondSyncRecords.isEmpty());
  }

  @Test
  public void testEmptyStateIncrementalIdenticalToFullRefresh() throws Exception {
    if (!sourceSupportsIncremental()) {
      return;
    }

    ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
    ConfiguredAirbyteCatalog fullRefreshCatalog = withFullRefreshSyncModes(configuredCatalog);

    final List<AirbyteRecordMessage> fullRefreshRecords = filterRecords(runRead(fullRefreshCatalog));
    final List<AirbyteRecordMessage> emptyStateRecords = filterRecords(runRead(configuredCatalog, Jsons.jsonNode(new HashMap<>())));

    assertFalse(fullRefreshRecords.isEmpty());
    assertFalse(emptyStateRecords.isEmpty());
    assertSameRecords(fullRefreshRecords, emptyStateRecords);
  }

  private List<AirbyteRecordMessage> filterRecords(Collection<AirbyteMessage> messages) {
    return messages.stream()
        .filter(m -> m.getType() == Type.RECORD)
        .map(AirbyteMessage::getRecord)
        .collect(Collectors.toList());
  }

  private ConfiguredAirbyteCatalog withSourceDefinedCursors(ConfiguredAirbyteCatalog catalog) {
    ConfiguredAirbyteCatalog clone = Jsons.clone(catalog);
    for (ConfiguredAirbyteStream configuredStream : clone.getStreams()) {
      if (configuredStream.getSyncMode() == INCREMENTAL && configuredStream.getStream().getSourceDefinedCursor()) {
        configuredStream.setCursorField(configuredStream.getStream().getDefaultCursorField());
      }
    }
    return clone;
  }

  private ConfiguredAirbyteCatalog withFullRefreshSyncModes(ConfiguredAirbyteCatalog catalog) {
    ConfiguredAirbyteCatalog clone = Jsons.clone(catalog);
    for (ConfiguredAirbyteStream configuredStream : clone.getStreams()) {
      if (configuredStream.getStream().getSupportedSyncModes().contains(FULL_REFRESH)) {
        configuredStream.setSyncMode(FULL_REFRESH);
      }
    }
    return clone;
  }

  private boolean sourceSupportsIncremental() throws Exception {
    ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    for (ConfiguredAirbyteStream stream : catalog.getStreams()) {
      if (stream.getStream().getSupportedSyncModes().contains(INCREMENTAL)) {
        return true;
      }
    }
    return false;
  }

  private OutputAndStatus<StandardGetSpecOutput> runSpec() {
    return new DefaultGetSpecWorker(new AirbyteIntegrationLauncher(getImageName(), pbf))
        .run(new JobGetSpecConfig().withDockerImage(getImageName()), jobRoot);
  }

  private OutputAndStatus<StandardCheckConnectionOutput> runCheck() throws Exception {
    return new DefaultCheckConnectionWorker(new AirbyteIntegrationLauncher(getImageName(), pbf))
        .run(new StandardCheckConnectionInput().withConnectionConfiguration(getConfig()), jobRoot);
  }

  private OutputAndStatus<StandardDiscoverCatalogOutput> runDiscover() throws Exception {
    return new DefaultDiscoverCatalogWorker(new AirbyteIntegrationLauncher(getImageName(), pbf))
        .run(new StandardDiscoverCatalogInput().withConnectionConfiguration(getConfig()), jobRoot);
  }

  private List<AirbyteMessage> runRead(ConfiguredAirbyteCatalog configuredCatalog) throws Exception {
    return runRead(configuredCatalog, null);
  }

  // todo (cgardens) - assume no state since we are all full refresh right now.
  private List<AirbyteMessage> runRead(ConfiguredAirbyteCatalog catalog, JsonNode state) throws Exception {
    final StandardTapConfig tapConfig = new StandardTapConfig()
        .withConnectionId(UUID.randomUUID())
        .withSourceConnectionConfiguration(getConfig())
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withState(state == null ? null : new State().withState(state).withConnectionId(UUID.randomUUID()))
        .withCatalog(catalog);

    final AirbyteSource source = new DefaultAirbyteSource(new AirbyteIntegrationLauncher(getImageName(), pbf));
    final List<AirbyteMessage> messages = new ArrayList<>();

    source.start(tapConfig, jobRoot);
    while (!source.isFinished()) {
      source.attemptRead().ifPresent(messages::add);
    }
    source.close();

    return messages;
  }

  private void assertSameRecords(List<AirbyteRecordMessage> expected, List<AirbyteRecordMessage> actual) {
    List<AirbyteRecordMessage> prunedExpected = expected.stream().map(this::pruneEmittedAt).collect(Collectors.toList());
    List<AirbyteRecordMessage> prunedActual = actual.stream().map(this::pruneEmittedAt).collect(Collectors.toList());
    assertEquals(prunedExpected.size(), prunedActual.size());
    assertTrue(prunedExpected.containsAll(prunedActual));
    assertTrue(prunedActual.containsAll(prunedExpected));
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
