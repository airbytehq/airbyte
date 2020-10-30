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

package io.airbyte.integrations.base;

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
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
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
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class TestSource {

  private static final Logger LOGGER = LoggerFactory.getLogger(TestSource.class);

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
   * Catalog to be used when attempting read operations.
   *
   * @return the catalog
   * @throws Exception - do what must be done.
   */
  protected abstract AirbyteCatalog getCatalog() throws Exception;

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
   * Assume that the {@link TestSource#getConfig()} is valid.
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
   * {@link TestSource#getConfig()} is valid.
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
  public void testRead() throws Exception {
    final List<AirbyteMessage> allMessages = runRead(getCatalog());
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

  /**
   * Verify that the integration overwrites the first sync with the second sync.
   */
  @Test
  public void testSecondRead() throws Exception {
    final List<AirbyteMessage> recordMessagesFirstRun =
        runRead(getCatalog()).stream().filter(m -> m.getType() == Type.RECORD).collect(Collectors.toList());
    final List<AirbyteMessage> recordMessagesSecondRun =
        runRead(getCatalog()).stream().filter(m -> m.getType() == Type.RECORD).collect(Collectors.toList());
    // the worker validates the messages, so we just validate the message, so we do not need to validate
    // again (as long as we use the worker, which we will not want to do long term).
    assertFalse(recordMessagesFirstRun.isEmpty());
    assertFalse(recordMessagesSecondRun.isEmpty());
    assertSameMessages(recordMessagesSecondRun, recordMessagesSecondRun);
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

  // todo (cgardens) - assume no state since we are all full refresh right now.
  private List<AirbyteMessage> runRead(AirbyteCatalog catalog) throws Exception {
    final StandardTapConfig tapConfig = new StandardTapConfig()
        .withConnectionId(UUID.randomUUID())
        .withSourceConnectionConfiguration(getConfig())
        .withSyncMode(SyncMode.FULL_REFRESH)
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

  private void assertSameMessages(List<AirbyteMessage> expected, List<AirbyteMessage> actual) {
    // we want to ignore order in this comparison.
    assertEquals(expected.size(), actual.size());
    assertTrue(expected.containsAll(actual));
    assertTrue(actual.containsAll(expected));
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
