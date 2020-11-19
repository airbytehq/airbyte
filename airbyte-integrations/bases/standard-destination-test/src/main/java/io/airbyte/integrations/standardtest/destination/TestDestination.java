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
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.functional.CheckedFunction;
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
import io.airbyte.integrations.base.normalization.NormalizationRunnerFactory;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
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
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class TestDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(TestDestination.class);

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
   * @param streamName - name of the stream for which we are retrieving records.
   * @return All of the records in the destination at the time this method is invoked.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected abstract List<JsonNode> retrieveRecords(TestDestinationEnv testEnv, String streamName) throws Exception;

  /**
   * Override to return true to if the destination implements basic normalization and it should be
   * tested here.
   *
   * @return - a boolean.
   */
  protected boolean implementsBasicNormalization() {
    return false;
  }

  /**
   * Same idea as {@link #retrieveRecords(TestDestinationEnv, String)}. Except this method should pull
   * records from the table that contains the normalized records and convert them back into the data
   * as it would appear in an {@link AirbyteRecordMessage}. Only need to override this method if
   * {@link #implementsBasicNormalization} returns true.
   *
   * @param testEnv - information about the test environment.
   * @param streamName - name of the stream for which we are retrieving records.
   * @return All of the records in the destination at the time this method is invoked.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected List<JsonNode> retrieveNormalizedRecords(TestDestinationEnv testEnv, String streamName) throws Exception {
    throw new IllegalStateException("Not implemented");
  }

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
  void setUpInternal() throws Exception {
    Path testDir = Path.of("/tmp/airbyte_tests/");
    Files.createDirectories(testDir);
    final Path workspaceRoot = Files.createTempDirectory(testDir, "test");
    jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"));
    localRoot = Files.createTempDirectory(testDir, "output");
    LOGGER.info("jobRoot: {}", jobRoot);
    LOGGER.info("localRoot: {}", localRoot);
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
          Arguments.of("exchange_rate_messages.txt", "exchange_rate_catalog.json"),
          Arguments.of("edge_case_messages.txt", "edge_case_catalog.json")
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
    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    runSync(getConfig(), messages, configuredCatalog);

    assertSameMessages(messages, retrieveRecordsForCatalog(catalog));
  }

  /**
   * Verify that the integration successfully writes records successfully both raw and normalized.
   * Tests a wide variety of messages an schemas (aspirationally, anyway).
   */
  @ParameterizedTest
  @ArgumentsSource(DataArgumentsProvider.class)
  public void testSyncWithNormalization(String messagesFilename, String catalogFilename) throws Exception {
    if (!implementsBasicNormalization()) {
      return;
    }

    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    runSync(getConfigWithBasicNormalization(), messages, configuredCatalog);

    assertSameMessages(messages, retrieveRecordsForCatalog(catalog));
    assertSameMessages(messages, retrieveNormalizedRecordsForCatalog(catalog), true);
  }

  /**
   * Verify that the integration overwrites the first sync with the second sync.
   */
  @Test
  public void testSecondSync() throws Exception {
    final AirbyteCatalog catalog =
        Jsons.deserialize(MoreResources.readResource("exchange_rate_catalog.json"), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> firstSyncMessages = MoreResources.readResource("exchange_rate_messages.txt").lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    runSync(getConfig(), firstSyncMessages, configuredCatalog);

    final List<AirbyteMessage> secondSyncMessages = Lists.newArrayList(new AirbyteMessage()
        .withRecord(new AirbyteRecordMessage()
            .withStream(catalog.getStreams().get(0).getName())
            .withData(Jsons.jsonNode(ImmutableMap.builder()
                .put("date", "2020-03-31T00:00:00Z")
                .put("HKD", 10)
                .put("NZD", 700)
                .build()))));
    runSync(getConfig(), secondSyncMessages, configuredCatalog);
    assertSameMessages(secondSyncMessages, retrieveRecordsForCatalog(catalog));
  }

  private OutputAndStatus<StandardGetSpecOutput> runSpec() {
    return new DefaultGetSpecWorker(new AirbyteIntegrationLauncher(getImageName(), pbf))
        .run(new JobGetSpecConfig().withDockerImage(getImageName()), jobRoot);
  }

  private OutputAndStatus<StandardCheckConnectionOutput> runCheck(JsonNode config) {
    return new DefaultCheckConnectionWorker(new AirbyteIntegrationLauncher(getImageName(), pbf))
        .run(new StandardCheckConnectionInput().withConnectionConfiguration(config), jobRoot);
  }

  private void runSync(JsonNode config, List<AirbyteMessage> messages, ConfiguredAirbyteCatalog catalog) throws Exception {

    final StandardTargetConfig targetConfig = new StandardTargetConfig()
        .withConnectionId(UUID.randomUUID())
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withCatalog(catalog)
        .withDestinationConnectionConfiguration(config);

    final AirbyteDestination target = new DefaultAirbyteDestination(new AirbyteIntegrationLauncher(getImageName(), pbf));

    target.start(targetConfig, jobRoot);
    messages.forEach(message -> Exceptions.toRuntime(() -> target.accept(message)));
    target.notifyEndOfStream();
    target.close();
  }

  private List<AirbyteRecordMessage> retrieveNormalizedRecordsForCatalog(AirbyteCatalog catalog) throws Exception {
    return retrieveRecordsForCatalog(streamName -> retrieveNormalizedRecords(testEnv, streamName), catalog);
  }

  private List<AirbyteRecordMessage> retrieveRecordsForCatalog(AirbyteCatalog catalog) throws Exception {
    return retrieveRecordsForCatalog(streamName -> retrieveRecords(testEnv, streamName), catalog);
  }

  private List<AirbyteRecordMessage> retrieveRecordsForCatalog(CheckedFunction<String, List<JsonNode>, Exception> retriever, AirbyteCatalog catalog)
      throws Exception {
    final List<AirbyteRecordMessage> actualMessages = new ArrayList<>();
    final List<String> streamNames = catalog.getStreams()
        .stream()
        .map(AirbyteStream::getName)
        .collect(Collectors.toList());

    for (final String streamName : streamNames) {
      actualMessages.addAll(retriever.apply(streamName)
          .stream()
          .map(data -> new AirbyteRecordMessage().withStream(streamName).withData(data))
          .collect(Collectors.toList()));
    }

    return actualMessages;
  }

  private void assertSameMessages(List<AirbyteMessage> expected, List<AirbyteRecordMessage> actual) {
    assertSameMessages(expected, actual, false);
  }

  // ignores emitted at.
  private void assertSameMessages(List<AirbyteMessage> expected, List<AirbyteRecordMessage> actual, boolean pruneAirbyteInternalFields) {
    final List<AirbyteRecordMessage> expectedProcessed = expected.stream()
        .filter(message -> message.getType() == AirbyteMessage.Type.RECORD)
        .map(AirbyteMessage::getRecord)
        .peek(recordMessage -> recordMessage.setEmittedAt(null))
        .map(recordMessage -> pruneAirbyteInternalFields ? this.safePrune(recordMessage) : recordMessage)
        .collect(Collectors.toList());

    final List<AirbyteRecordMessage> actualProcessed = actual.stream()
        .map(recordMessage -> pruneAirbyteInternalFields ? this.safePrune(recordMessage) : recordMessage)
        .collect(Collectors.toList());
    assertSameData(expectedProcessed, actualProcessed);
  }

  private void assertSameData(List<AirbyteRecordMessage> expected, List<AirbyteRecordMessage> actual) {
    LOGGER.info("expected: {}", expected);
    LOGGER.info("actual: {}", actual);

    // we want to ignore order in this comparison.
    assertEquals(expected.size(), actual.size());
    assertTrue(expected.containsAll(actual));
    assertTrue(actual.containsAll(expected));
  }

  /**
   * Same as {@link #pruneMutate(JsonNode)}, except does a defensive copy and returns a new json node
   * object instead of mutating in place.
   *
   * @param record - record that will be pruned.
   * @return pruned json node.
   */
  private AirbyteRecordMessage safePrune(AirbyteRecordMessage record) {
    final AirbyteRecordMessage clone = Jsons.clone(record);
    pruneMutate(clone.getData());
    return clone;
  }

  /**
   * Prune fields that are added internally by airbyte and are not part of the original data. Used so
   * that we can compare data that is persisted by an Airbyte worker to the original data. This method
   * mutates the provided json in place.
   *
   * @param json - json that will be pruned. will be mutated in place!
   */
  private void pruneMutate(JsonNode json) {
    for (final String key : Jsons.keys(json)) {
      final JsonNode node = json.get(key);
      // recursively prune all airbyte internal fields.
      if (node.isObject() || node.isArray()) {
        pruneMutate(node);
      }

      // prune the following
      // - airbyte internal fields
      // - fields that match what airbyte generates as hash ids
      // - null values -- normalization will often return `<key>: null` but in the original data that key
      // likely did not exist in the original message. the most consistent thing to do is always remove
      // the null fields (this choice does decrease our ability to check that normalization creates
      // columns even if all the values in that column are null)
      if (Sets.newHashSet("emitted_at", "ab_id", "normalized_at").contains(key) || key.matches("^_.*_hashid$") || json.get(key).isNull()) {
        ((ObjectNode) json).remove(key);
      }
    }
  }

  private JsonNode getConfigWithBasicNormalization() throws Exception {
    final JsonNode config = getConfig();
    ((ObjectNode) config).put(NormalizationRunnerFactory.BASIC_NORMALIZATION_KEY, true);
    return config;
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
