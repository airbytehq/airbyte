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

package io.airbyte.integrations.standardtest.destination;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.config.StandardSync.SyncMode;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.workers.DefaultCheckConnectionWorker;
import io.airbyte.workers.DefaultGetSpecWorker;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessBuilderFactory;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteDestination;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteDestination;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;

public abstract class TestDestination {

  private TestDestinationEnv testEnv;

  private Path jobRoot;
  protected Path localRoot;
  private ProcessBuilderFactory pbf;

  private static final Set<String> ALL_RAW_STREAM_NAMES = Sets.newHashSet(
      "exchange_rate");

  /**
   * Name of the docker image that the tests will run against.
   *
   * @return docker image name
   */
  protected abstract String getImageName();

  /**
   * Configuration specific to the integration. Will be passed to integration where appropriate in
   * each test. Should be valid.
   *
   * @return integration-specific configuration
   */
  protected abstract JsonNode getConfig() throws Exception;

  /**
   * Configuration specific to the integration. Will be passed to integration where appropriate in
   * tests that test behavior when configuration is invalid. e.g incorrect password. Should be
   * invalid.
   *
   * @return integration-specific configuration
   */
  protected abstract JsonNode getFailCheckConfig() throws Exception;

  /**
   * Function that returns all of the records in destination as json at the time this method is
   * invoked. These will be used to check that the data actually written is what should actually be
   * there. Note: this returns a set and does not test any order guarantees.
   *
   * @param testEnv - information about the test environment.
   * @return All of the records in the destination at the time this method is invoked.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected abstract List<JsonNode> retrieveRecords(TestDestinationEnv testEnv, String streamName) throws Exception;

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

  /**
   * Function that is applied to stream names in destination tests before emitting records/schemas.
   * This is useful if there's a non-trivial amount of setup involved for the integration or it isn't
   * easy to namespace.
   *
   * @return - function to transform resource (usually the identity function)
   */
  protected Function<String, String> streamRenamer() {
    return Function.identity();
  }

  protected Set<String> getAllStreamNames() {
    return ALL_RAW_STREAM_NAMES.stream()
        .map(x -> streamRenamer().apply(x))
        .collect(Collectors.toSet());
  }

  @BeforeEach
  void setUpInternal() throws Exception {
    Path testDir = Path.of("/tmp/airbyte_tests/");
    Files.createDirectories(testDir);
    final Path workspaceRoot = Files.createTempDirectory(testDir, "test");
    jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"));
    localRoot = Files.createTempDirectory(testDir, "output");
    testEnv = new TestDestinationEnv(localRoot);

    setup(testEnv);

    pbf = new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), localRoot.toString(), "host");
  }

  @AfterEach
  void tearDownInternal() throws Exception {
    tearDown(testEnv);
  }

  /**
   * Verify that when the integrations returns a valid spec.
   */
  @Test
  public void testGetSpec() {
    final OutputAndStatus<StandardGetSpecOutput> output = runSpec();
    assertTrue(output.getOutput().isPresent());
  }

  /**
   * Verify that when given valid credentials, that check connection returns a success response.
   * Assume that the {@link TestDestination#getConfig()} is valid.
   */
  @Test
  public void testCheckConnection() throws Exception {
    final OutputAndStatus<StandardCheckConnectionOutput> output = runCheck(getConfig());
    assertTrue(output.getOutput().isPresent());
    assertEquals(Status.SUCCEEDED, output.getOutput().get().getStatus());
  }

  /**
   * Verify that when given invalid credentials, that check connection returns a failed response.
   * Assume that the {@link TestDestination#getFailCheckConfig()} is invalid.
   */
  @Test
  public void testCheckConnectionInvalidCredentials() throws Exception {
    final OutputAndStatus<StandardCheckConnectionOutput> output = runCheck(getFailCheckConfig());
    assertTrue(output.getOutput().isPresent());
    assertEquals(Status.FAILED, output.getOutput().get().getStatus());
  }

  private static class DataArgumentsProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(ExtensionContext context) {
      return Stream.of(
          Arguments.of("exchange_rate_messages.txt", "exchange_rate_catalog.json")
      // todo - need to use the new protocol to capture this.
      // Arguments.of("stripe_messages.txt", "stripe_schema.json")
      );
    }

  }

  /**
   * Verify that the integration successfully writes records. Tests a wide variety of messages and
   * schemas (aspirationally, anyway).
   */
  @ParameterizedTest
  @ArgumentsSource(DataArgumentsProvider.class)
  public void testSync(String messagesFilename, String catalogFilename) throws Exception {
    final AirbyteCatalog catalog = Jsons.deserialize(renameAllStreams(MoreResources.readResource(catalogFilename)), AirbyteCatalog.class);
    final List<AirbyteMessage> messages = renameAllStreams(MoreResources.readResource(messagesFilename)).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    runSync(messages, catalog);

    assertSameMessages(messages, retrieveRecords(testEnv, catalog.getStreams().get(0).getName()));
  }

  /**
   * Verify that the integration overwrites the first sync with the second sync.
   */
  @Test
  public void testSecondSync() throws Exception {
    final AirbyteCatalog catalog =
        Jsons.deserialize(renameAllStreams(MoreResources.readResource("exchange_rate_catalog.json")), AirbyteCatalog.class);
    final List<AirbyteMessage> firstSyncMessages = renameAllStreams(MoreResources.readResource("exchange_rate_messages.txt")).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    runSync(firstSyncMessages, catalog);

    List<AirbyteMessage> secondSyncMessages = Lists.newArrayList(new AirbyteMessage()
        .withRecord(new AirbyteRecordMessage()
            .withStream(catalog.getStreams().get(0).getName())
            .withData(Jsons.jsonNode(ImmutableMap.builder()
                .put("date", "2020-03-31T00:00:00Z")
                .put("HKD", 10)
                .put("NZD", 700)
                .build()))));
    runSync(secondSyncMessages, catalog);
    assertSameMessages(secondSyncMessages, retrieveRecords(testEnv, catalog.getStreams().get(0).getName()));
  }

  private OutputAndStatus<StandardGetSpecOutput> runSpec() {
    return new DefaultGetSpecWorker(new AirbyteIntegrationLauncher(getImageName(), pbf))
        .run(new JobGetSpecConfig().withDockerImage(getImageName()), jobRoot);
  }

  private OutputAndStatus<StandardCheckConnectionOutput> runCheck(JsonNode config) {
    return new DefaultCheckConnectionWorker(new AirbyteIntegrationLauncher(getImageName(), pbf))
        .run(new StandardCheckConnectionInput().withConnectionConfiguration(config), jobRoot);
  }

  // todo (cgardens) - still uses the old schema.
  private void runSync(List<AirbyteMessage> messages, AirbyteCatalog catalog) throws Exception {
    final StandardTargetConfig targetConfig = new StandardTargetConfig()
        .withConnectionId(UUID.randomUUID())
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withCatalog(catalog)
        .withDestinationConnectionConfiguration(getConfig());

    final AirbyteDestination target = new DefaultAirbyteDestination(new AirbyteIntegrationLauncher(getImageName(), pbf));

    target.start(targetConfig, jobRoot);
    messages.forEach(message -> Exceptions.toRuntime(() -> target.accept(message)));
    target.notifyEndOfStream();
    target.close();
  }

  private void assertSameMessages(List<AirbyteMessage> expected, List<JsonNode> actual) {
    final List<JsonNode> expectedJson = expected.stream()
        .filter(message -> message.getType() == AirbyteMessage.Type.RECORD)
        .map(AirbyteMessage::getRecord)
        .map(AirbyteRecordMessage::getData)
        .collect(Collectors.toList());

    // we want to ignore order in this comparison.
    assertEquals(expectedJson.size(), actual.size());
    assertTrue(expectedJson.containsAll(actual));
    assertTrue(actual.containsAll(expectedJson));
  }

  private String renameAllStreams(String input) {
    String output = input;

    for (String streamName : ALL_RAW_STREAM_NAMES) {
      final String newStreamName = streamRenamer().apply(streamName);
      output = output.replace(streamName, newStreamName);
    }

    return output;
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
