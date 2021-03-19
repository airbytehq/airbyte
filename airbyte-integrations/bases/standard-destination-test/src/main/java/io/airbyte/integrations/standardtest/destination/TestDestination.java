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
import static org.junit.jupiter.api.Assertions.assertNotNull;
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
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream.DestinationSyncMode;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.workers.DefaultCheckConnectionWorker;
import io.airbyte.workers.DefaultGetSpecWorker;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.normalization.NormalizationRunner;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessBuilderFactory;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteDestination;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteDestination;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
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

  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;

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
   * Detects if a destination implements incremental mode from the spec.json that should include
   * 'supportsIncremental' = true
   *
   * @return - a boolean.
   */
  protected boolean implementsIncremental() throws WorkerException {
    final ConnectorSpecification spec = runSpec();
    assertNotNull(spec);
    if (spec.getSupportsIncremental() != null) {
      return spec.getSupportsIncremental();
    } else {
      return false;
    }
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

  protected List<String> resolveIdentifier(String identifier) {
    final List<String> result = new ArrayList<>();
    result.add(identifier);
    return result;
  }

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
  public void testGetSpec() throws WorkerException {
    assertNotNull(runSpec());
  }

  /**
   * Verify that when given valid credentials, that check connection returns a success response.
   * Assume that the {@link TestDestination#getConfig()} is valid.
   */
  @Test
  public void testCheckConnection() throws Exception {
    assertEquals(Status.SUCCEEDED, runCheck(getConfig()).getStatus());
  }

  /**
   * Verify that when given invalid credentials, that check connection returns a failed response.
   * Assume that the {@link TestDestination#getFailCheckConfig()} is invalid.
   */
  @Test
  public void testCheckConnectionInvalidCredentials() throws Exception {
    assertEquals(Status.FAILED, runCheck(getFailCheckConfig()).getStatus());
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
   * Verify that the integration successfully writes records incrementally. The second run should
   * append records to the datastore instead of overwriting the previous run.
   */
  @Test
  public void testIncrementalSync() throws Exception {
    if (!implementsIncremental()) {
      LOGGER.info("Destination's spec.json does not include '\"supportsIncremental\" ; true'");
      return;
    }

    testIncrementalSync("exchange_rate_messages.txt", "exchange_rate_catalog.json");
  }

  public void testIncrementalSync(String messagesFilename, String catalogFilename) throws Exception {
    final AirbyteCatalog catalog =
        Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    configuredCatalog.getStreams().forEach(s -> {
      s.withSyncMode(SyncMode.INCREMENTAL);
      s.withDestinationSyncMode(DestinationSyncMode.APPEND);
    });
    final List<AirbyteMessage> firstSyncMessages = MoreResources.readResource(messagesFilename).lines()
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
    final List<AirbyteMessage> expectedMessagesAfterSecondSync = new ArrayList<>();
    expectedMessagesAfterSecondSync.addAll(firstSyncMessages);
    expectedMessagesAfterSecondSync.addAll(secondSyncMessages);
    assertSameMessages(expectedMessagesAfterSecondSync, retrieveRecordsForCatalog(catalog));
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

    LOGGER.info("Comparing retrieveRecordsForCatalog for {} and {}", messagesFilename, catalogFilename);
    assertSameMessages(messages, retrieveRecordsForCatalog(catalog));
    LOGGER.info("Comparing retrieveNormalizedRecordsForCatalog for {} and {}", messagesFilename, catalogFilename);
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

  private ConnectorSpecification runSpec() throws WorkerException {
    return new DefaultGetSpecWorker(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), pbf))
        .run(new JobGetSpecConfig().withDockerImage(getImageName()), jobRoot);
  }

  private StandardCheckConnectionOutput runCheck(JsonNode config) throws WorkerException {
    return new DefaultCheckConnectionWorker(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), pbf))
        .run(new StandardCheckConnectionInput().withConnectionConfiguration(config), jobRoot);
  }

  private void runSync(JsonNode config, List<AirbyteMessage> messages, ConfiguredAirbyteCatalog catalog) throws Exception {

    final StandardTargetConfig targetConfig = new StandardTargetConfig()
        .withConnectionId(UUID.randomUUID())
        .withCatalog(catalog)
        .withDestinationConnectionConfiguration(config);

    final AirbyteDestination target = new DefaultAirbyteDestination(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), pbf));

    target.start(targetConfig, jobRoot);
    messages.forEach(message -> Exceptions.toRuntime(() -> target.accept(message)));
    target.notifyEndOfStream();
    target.close();

    // skip if basic normalization is not configured to run (either not set or false).
    if (!config.hasNonNull(WorkerConstants.BASIC_NORMALIZATION_KEY) || !config.get(WorkerConstants.BASIC_NORMALIZATION_KEY).asBoolean()) {
      return;
    }

    final NormalizationRunner runner = NormalizationRunnerFactory.create(
        getImageName(),
        pbf, targetConfig.getDestinationConnectionConfiguration());
    runner.start();
    final Path normalizationRoot = Files.createDirectories(jobRoot.resolve("normalize"));
    if (!runner.normalize(JOB_ID, JOB_ATTEMPT, normalizationRoot, targetConfig.getDestinationConnectionConfiguration(), targetConfig.getCatalog())) {
      throw new WorkerException("Normalization Failed.");
    }
    runner.close();
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
    final List<JsonNode> expectedProcessed = expected.stream()
        .filter(message -> message.getType() == AirbyteMessage.Type.RECORD)
        .map(AirbyteMessage::getRecord)
        .peek(recordMessage -> recordMessage.setEmittedAt(null))
        .map(recordMessage -> pruneAirbyteInternalFields ? safePrune(recordMessage) : recordMessage)
        .map(recordMessage -> recordMessage.getData())
        .collect(Collectors.toList());

    final List<JsonNode> actualProcessed = actual.stream()
        .map(recordMessage -> pruneAirbyteInternalFields ? safePrune(recordMessage) : recordMessage)
        .map(recordMessage -> recordMessage.getData())
        .collect(Collectors.toList());

    assertSameData(expectedProcessed, actualProcessed);
  }

  private void assertSameData(List<JsonNode> expected, List<JsonNode> actual) {
    LOGGER.info("Expected data {}", expected);
    LOGGER.info("Actual data   {}", actual);
    assertEquals(expected.size(), actual.size());
    final Iterator<JsonNode> expectedIterator = expected.iterator();
    final Iterator<JsonNode> actualIterator = actual.iterator();
    while (expectedIterator.hasNext() && actualIterator.hasNext()) {
      final JsonNode expectedData = expectedIterator.next();
      final JsonNode actualData = actualIterator.next();
      final Iterator<Entry<String, JsonNode>> expectedDataIterator = expectedData.fields();
      LOGGER.info("Expected row {}", expectedData);
      LOGGER.info("Actual row   {}", actualData);
      assertEquals(expectedData.size(), actualData.size());
      while (expectedDataIterator.hasNext()) {
        final Entry<String, JsonNode> expectedEntry = expectedDataIterator.next();
        final JsonNode expectedValue = expectedEntry.getValue();
        JsonNode actualValue = null;
        String key = expectedEntry.getKey();
        for (String tmpKey : resolveIdentifier(expectedEntry.getKey())) {
          actualValue = actualData.get(tmpKey);
          if (actualValue != null) {
            key = tmpKey;
            break;
          }
        }
        LOGGER.info("For {} Expected {} vs Actual {}", key, expectedValue, actualValue);
        assertTrue(actualData.has(key));
        assertEquals(expectedValue, actualValue);
      }
    }
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
      final HashSet<String> airbyteInternalFields = Sets.newHashSet(
          "emitted_at",
          "ab_id",
          "normalized_at",
          "EMITTED_AT",
          "AB_ID",
          "NORMALIZED_AT",
          "HASHID");
      if (airbyteInternalFields.stream().anyMatch(internalField -> key.toLowerCase().contains(internalField.toLowerCase()))
          || json.get(key).isNull()) {
        ((ObjectNode) json).remove(key);
      }
    }
  }

  private JsonNode getConfigWithBasicNormalization() throws Exception {
    final JsonNode config = getConfig();
    ((ObjectNode) config).put(WorkerConstants.BASIC_NORMALIZATION_KEY, true);
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
