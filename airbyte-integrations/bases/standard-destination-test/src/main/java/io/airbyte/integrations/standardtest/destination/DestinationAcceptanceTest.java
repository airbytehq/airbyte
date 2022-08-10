/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.fail;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.commons.util.MoreLists;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.standardtest.destination.comparator.BasicTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.general.DbtTransformationRunner;
import io.airbyte.workers.general.DefaultCheckConnectionWorker;
import io.airbyte.workers.general.DefaultGetSpecWorker;
import io.airbyte.workers.helper.EntrypointEnvChecker;
import io.airbyte.workers.internal.AirbyteDestination;
import io.airbyte.workers.internal.DefaultAirbyteDestination;
import io.airbyte.workers.normalization.NormalizationRunner;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Random;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.joda.time.DateTime;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class DestinationAcceptanceTest {

  private static final Random RANDOM = new Random();
  private static final String NORMALIZATION_VERSION = "dev";

  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;

  private static final String DUMMY_CATALOG_NAME = "DummyCatalog";

  private static final Logger LOGGER = LoggerFactory.getLogger(DestinationAcceptanceTest.class);

  private TestDestinationEnv testEnv;

  private Path jobRoot;
  private ProcessFactory processFactory;
  private WorkerConfigs workerConfigs;

  protected Path localRoot;
  protected TestDataComparator testDataComparator = getTestDataComparator();

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
   * @param namespace - the destination namespace records are located in. Null if not applicable.
   *        Usually a JDBC schema.
   * @param streamSchema - schema of the stream to be retrieved. This is only necessary for
   *        destinations in which data types cannot be accurately inferred (e.g. in CSV destination,
   *        every value is a string).
   * @return All of the records in the destination at the time this method is invoked.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected abstract List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                                    String streamName,
                                                    String namespace,
                                                    JsonNode streamSchema)
      throws Exception;

  /**
   * Returns a destination's default schema. The default implementation assumes this corresponds to
   * the configuration's 'schema' field, as this is how most of our destinations implement this.
   * Destinations are free to appropriately override this. The return value is used to assert
   * correctness.
   *
   * If not applicable, Destinations are free to ignore this.
   *
   * @param config - integration-specific configuration returned by {@link #getConfig()}.
   * @return the default schema, if applicatble.
   */
  protected String getDefaultSchema(final JsonNode config) throws Exception {
    if (config.get("schema") == null) {
      return null;
    }
    return config.get("schema").asText();
  }

  /**
   * Override to return true if a destination implements namespaces and should be tested as such.
   */
  protected boolean implementsNamespaces() {
    return false;
  }

  /**
   * Detects if a destination implements append mode from the spec.json that should include
   * 'supportsIncremental' = true
   *
   * @return - a boolean.
   */
  protected boolean implementsAppend() throws WorkerException {
    final ConnectorSpecification spec = runSpec();
    assertNotNull(spec);
    if (spec.getSupportsIncremental() != null) {
      return spec.getSupportsIncremental();
    } else {
      return false;
    }
  }

  protected boolean normalizationFromSpec() throws Exception {
    final ConnectorSpecification spec = runSpec();
    assertNotNull(spec);
    if (spec.getSupportsNormalization() != null) {
      return spec.getSupportsNormalization();
    } else {
      return false;
    }
  }

  protected boolean dbtFromSpec() throws WorkerException {
    final ConnectorSpecification spec = runSpec();
    assertNotNull(spec);
    if (spec.getSupportsDBT() != null) {
      return spec.getSupportsDBT();
    } else {
      return false;
    }
  }

  /**
   * Detects if a destination implements append dedup mode from the spec.json that should include
   * 'supportedDestinationSyncMode'
   *
   * @return - a boolean.
   */
  protected boolean implementsAppendDedup() throws WorkerException {
    final ConnectorSpecification spec = runSpec();
    assertNotNull(spec);
    if (spec.getSupportedDestinationSyncModes() != null) {
      return spec.getSupportedDestinationSyncModes().contains(DestinationSyncMode.APPEND_DEDUP);
    } else {
      return false;
    }
  }

  /**
   * Detects if a destination implements overwrite mode from the spec.json that should include
   * 'supportedDestinationSyncMode'
   *
   * @return - a boolean.
   */
  protected boolean implementsOverwrite() throws WorkerException {
    final ConnectorSpecification spec = runSpec();
    assertNotNull(spec);
    if (spec.getSupportedDestinationSyncModes() != null) {
      return spec.getSupportedDestinationSyncModes().contains(DestinationSyncMode.OVERWRITE);
    } else {
      return false;
    }
  }

  /**
   * Override to return true to if the destination implements basic normalization and it should be
   * tested here.
   *
   * @return - a boolean.
   */
  protected boolean supportsNormalization() {
    return false;
  }

  protected boolean supportsDBT() {
    return false;
  }

  /**
   * Override to return true if a destination implements size limits on record size (then destination
   * should redefine getMaxRecordValueLimit() too)
   */
  protected boolean implementsRecordSizeLimitChecks() {
    return false;
  }

  /**
   * Same idea as {@link #retrieveRecords(TestDestinationEnv, String, String, JsonNode)}. Except this
   * method should pull records from the table that contains the normalized records and convert them
   * back into the data as it would appear in an {@link AirbyteRecordMessage}. Only need to override
   * this method if {@link #normalizationFromSpec} returns true.
   *
   * @param testEnv - information about the test environment.
   * @param streamName - name of the stream for which we are retrieving records.
   * @param namespace - the destination namespace records are located in. Null if not applicable.
   *        Usually a JDBC schema.
   * @return All of the records in the destination at the time this method is invoked.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace)
      throws Exception {
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

  /**
   * @deprecated This method is moved to the AdvancedTestDataComparator. Please move your destination
   *             implementation of the method to your comparator implementation.
   */
  @Deprecated
  protected List<String> resolveIdentifier(final String identifier) {
    return List.of(identifier);
  }

  @BeforeEach
  void setUpInternal() throws Exception {
    final Path testDir = Path.of("/tmp/airbyte_tests/");
    Files.createDirectories(testDir);
    final Path workspaceRoot = Files.createTempDirectory(testDir, "test");
    jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"));
    localRoot = Files.createTempDirectory(testDir, "output");
    LOGGER.info("jobRoot: {}", jobRoot);
    LOGGER.info("localRoot: {}", localRoot);
    testEnv = new TestDestinationEnv(localRoot);
    workerConfigs = new WorkerConfigs(new EnvConfigs());

    setup(testEnv);

    processFactory = new DockerProcessFactory(workerConfigs, workspaceRoot, workspaceRoot.toString(), localRoot.toString(), "host");
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
   * Assume that the {@link DestinationAcceptanceTest#getConfig()} is valid.
   */
  @Test
  public void testCheckConnection() throws Exception {
    assertEquals(Status.SUCCEEDED, runCheck(getConfig()).getStatus());
  }

  /**
   * Verify that when given invalid credentials, that check connection returns a failed response.
   * Assume that the {@link DestinationAcceptanceTest#getFailCheckConfig()} is invalid.
   */
  @Test
  public void testCheckConnectionInvalidCredentials() throws Exception {
    assertEquals(Status.FAILED, runCheck(getFailCheckConfig()).getStatus());
  }

  /**
   * Verify that the integration successfully writes records. Tests a wide variety of messages and
   * schemas (aspirationally, anyway).
   */
  @ParameterizedTest
  @ArgumentsSource(DataArgumentsProvider.class)
  public void testSync(final String messagesFilename, final String catalogFilename) throws Exception {
    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());

    final JsonNode config = getConfig();
    final String defaultSchema = getDefaultSchema(config);
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false);
    retrieveRawRecordsAndAssertSameMessages(catalog, messages, defaultSchema);
  }

  /**
   * This serves to test MSSQL 2100 limit parameters in a single query. this means that for Airbyte
   * insert data need to limit to ~ 700 records (3 columns for the raw tables) = 2100 params
   */
  @ParameterizedTest
  @ArgumentsSource(DataArgumentsProvider.class)
  public void testSyncWithLargeRecordBatch(final String messagesFilename, final String catalogFilename) throws Exception {
    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());

    final List<AirbyteMessage> largeNumberRecords = Collections
        .nCopies(400, messages)
        .stream()
        .flatMap(List::stream)
        // regroup messages per stream
        .sorted(Comparator
            .comparing(AirbyteMessage::getType)
            .thenComparing(message -> message.getType().equals(Type.RECORD) ? message.getRecord().getStream() : message.toString()))
        .collect(Collectors.toList());

    final JsonNode config = getConfig();
    runSyncAndVerifyStateOutput(config, largeNumberRecords, configuredCatalog, false);
  }

  /**
   * Verify that the integration overwrites the first sync with the second sync.
   */
  @Test
  public void testSecondSync() throws Exception {
    if (!implementsOverwrite()) {
      LOGGER.info("Destination's spec.json does not support overwrite sync mode.");
      return;
    }

    final AirbyteCatalog catalog =
        Jsons.deserialize(MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.catalogFile), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);

    final List<AirbyteMessage> firstSyncMessages = MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.messageFile).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    final JsonNode config = getConfig();
    runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredCatalog, false);

    // We need to make sure that other streams\tables\files in the same location will not be
    // affected\deleted\overridden by our activities during first, second or any future sync.
    // So let's create a dummy data that will be checked after all sync. It should remain the same
    final AirbyteCatalog dummyCatalog =
        Jsons.deserialize(MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.catalogFile), AirbyteCatalog.class);
    dummyCatalog.getStreams().get(0).setName(DUMMY_CATALOG_NAME);
    final ConfiguredAirbyteCatalog configuredDummyCatalog = CatalogHelpers.toDefaultConfiguredCatalog(dummyCatalog);
    // update messages to set new dummy stream name
    firstSyncMessages.stream().filter(message -> message.getRecord() != null)
        .forEach(message -> message.getRecord().setStream(DUMMY_CATALOG_NAME));
    // sync dummy data
    runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredDummyCatalog, false);

    // Run second sync
    final List<AirbyteMessage> secondSyncMessages = Lists.newArrayList(
        new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(catalog.getStreams().get(0).getName())
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.builder()
                    .put("id", 1)
                    .put("currency", "USD")
                    .put("date", "2020-03-31T00:00:00Z")
                    // TODO(sherifnada) hack: write decimals with sigfigs because Snowflake stores 10.1 as "10" which
                    // fails destination tests
                    .put("HKD", 10.1)
                    .put("NZD", 700.1)
                    .build()))),
        new AirbyteMessage()
            .withType(Type.STATE)
            .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))));

    runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog, false);
    final String defaultSchema = getDefaultSchema(config);
    retrieveRawRecordsAndAssertSameMessages(catalog, secondSyncMessages, defaultSchema);

    // verify that other streams in the same location were not affected. If something fails here,
    // then this need to be fixed in connectors logic to override only required streams
    retrieveRawRecordsAndAssertSameMessages(dummyCatalog, firstSyncMessages, defaultSchema);
  }

  /**
   * Tests that we are able to read over special characters properly when processing line breaks in
   * destinations.
   */
  @Test
  public void testLineBreakCharacters() throws Exception {
    final AirbyteCatalog catalog =
        Jsons.deserialize(MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.catalogFile), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final JsonNode config = getConfig();

    final List<AirbyteMessage> secondSyncMessages = Lists.newArrayList(
        new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(catalog.getStreams().get(0).getName())
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.builder()
                    .put("id", 1)
                    .put("currency", "USD\u2028")
                    .put("date", "2020-03-\n31T00:00:00Z\r")
                    // TODO(sherifnada) hack: write decimals with sigfigs because Snowflake stores 10.1 as "10" which
                    // fails destination tests
                    .put("HKD", 10.1)
                    .put("NZD", 700.1)
                    .build()))),
        new AirbyteMessage()
            .withType(Type.STATE)
            .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))));

    runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog, false);
    final String defaultSchema = getDefaultSchema(config);
    retrieveRawRecordsAndAssertSameMessages(catalog, secondSyncMessages, defaultSchema);
  }

  @Test
  public void specNormalizationValueShouldBeCorrect() throws Exception {
    final boolean normalizationFromSpec = normalizationFromSpec();
    assertEquals(normalizationFromSpec, supportsNormalization());
    if (normalizationFromSpec) {
      boolean normalizationRunnerFactorySupportsDestinationImage;
      try {
        NormalizationRunnerFactory.create(workerConfigs, getImageName(), processFactory, NORMALIZATION_VERSION);
        normalizationRunnerFactorySupportsDestinationImage = true;
      } catch (final IllegalStateException e) {
        normalizationRunnerFactorySupportsDestinationImage = false;
      }
      assertEquals(normalizationFromSpec, normalizationRunnerFactorySupportsDestinationImage);
    }
  }

  @Test
  public void specDBTValueShouldBeCorrect() throws WorkerException {
    assertEquals(dbtFromSpec(), supportsDBT());
  }

  /**
   * Verify that the integration successfully writes records incrementally. The second run should
   * append records to the datastore instead of overwriting the previous run.
   */
  @Test
  public void testIncrementalSync() throws Exception {
    if (!implementsAppend()) {
      LOGGER.info("Destination's spec.json does not include '\"supportsIncremental\" ; true'");
      return;
    }

    final AirbyteCatalog catalog =
        Jsons.deserialize(MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.catalogFile), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    configuredCatalog.getStreams().forEach(s -> {
      s.withSyncMode(SyncMode.INCREMENTAL);
      s.withDestinationSyncMode(DestinationSyncMode.APPEND);
    });

    final List<AirbyteMessage> firstSyncMessages = MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.messageFile).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    final JsonNode config = getConfig();
    runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredCatalog, false);
    final List<AirbyteMessage> secondSyncMessages = Lists.newArrayList(
        new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(catalog.getStreams().get(0).getName())
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.builder()
                    .put("id", 1)
                    .put("currency", "USD")
                    .put("date", "2020-03-31T00:00:00Z")
                    // TODO(sherifnada) hack: write decimals with sigfigs because Snowflake stores 10.1 as "10" which
                    // fails destination tests
                    .put("HKD", 10.1)
                    .put("NZD", 700.1)
                    .build()))),
        new AirbyteMessage()
            .withType(Type.STATE)
            .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))));
    runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog, false);

    final List<AirbyteMessage> expectedMessagesAfterSecondSync = new ArrayList<>();
    expectedMessagesAfterSecondSync.addAll(firstSyncMessages);
    expectedMessagesAfterSecondSync.addAll(secondSyncMessages);

    final String defaultSchema = getDefaultSchema(config);
    retrieveRawRecordsAndAssertSameMessages(catalog, expectedMessagesAfterSecondSync, defaultSchema);
  }

  /**
   * Verify that the integration successfully writes records successfully both raw and normalized.
   * Tests a wide variety of messages an schemas (aspirationally, anyway).
   */
  @ParameterizedTest
  @ArgumentsSource(DataArgumentsProvider.class)
  public void testSyncWithNormalization(final String messagesFilename, final String catalogFilename) throws Exception {
    if (!normalizationFromSpec()) {
      return;
    }

    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());

    final JsonNode config = getConfig();
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true);

    final String defaultSchema = getDefaultSchema(config);
    final List<AirbyteRecordMessage> actualMessages = retrieveNormalizedRecords(catalog, defaultSchema);
    assertSameMessages(messages, actualMessages, true);
  }

  /**
   * Verify that the integration successfully writes records successfully both raw and normalized and
   * run dedupe transformations.
   *
   * Although this test assumes append-dedup requires normalization, and almost all our Destinations
   * do so, this is not necessarily true. This explains {@link #implementsAppendDedup()}.
   */
  @Test
  public void testIncrementalDedupeSync() throws Exception {
    if (!implementsAppendDedup()) {
      LOGGER.info("Destination's spec.json does not include 'append_dedupe' in its '\"supportedDestinationSyncModes\"'");
      return;
    }

    final AirbyteCatalog catalog =
        Jsons.deserialize(MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.catalogFile), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    configuredCatalog.getStreams().forEach(s -> {
      s.withSyncMode(SyncMode.INCREMENTAL);
      s.withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP);
      s.withCursorField(Collections.emptyList());
      // use composite primary key of various types (string, float)
      s.withPrimaryKey(List.of(List.of("id"), List.of("currency"), List.of("date"), List.of("NZD")));
    });

    final List<AirbyteMessage> firstSyncMessages = MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.messageFile).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    final JsonNode config = getConfig();
    runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredCatalog, true);

    final List<AirbyteMessage> secondSyncMessages = Lists.newArrayList(
        new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(catalog.getStreams().get(0).getName())
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.builder()
                    .put("id", 2)
                    .put("currency", "EUR")
                    .put("date", "2020-09-01T00:00:00Z")
                    .put("HKD", 10.5)
                    .put("NZD", 1.14)
                    .build()))),
        new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(catalog.getStreams().get(0).getName())
                .withEmittedAt(Instant.now().toEpochMilli() + 100L)
                .withData(Jsons.jsonNode(ImmutableMap.builder()
                    .put("id", 1)
                    .put("currency", "USD")
                    .put("date", "2020-09-01T00:00:00Z")
                    .put("HKD", 5.4)
                    .put("NZD", 1.14)
                    .build()))),
        new AirbyteMessage()
            .withType(Type.STATE)
            .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))));
    runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog, true);

    final List<AirbyteMessage> expectedMessagesAfterSecondSync = new ArrayList<>();
    expectedMessagesAfterSecondSync.addAll(firstSyncMessages);
    expectedMessagesAfterSecondSync.addAll(secondSyncMessages);

    final Map<String, AirbyteMessage> latestMessagesOnly = expectedMessagesAfterSecondSync
        .stream()
        .filter(message -> message.getType() == Type.RECORD && message.getRecord() != null)
        .collect(Collectors.toMap(
            message -> message.getRecord().getData().get("id").asText() +
                message.getRecord().getData().get("currency").asText() +
                message.getRecord().getData().get("date").asText() +
                message.getRecord().getData().get("NZD").asText(),
            message -> message,
            // keep only latest emitted record message per primary key/cursor
            (a, b) -> a.getRecord().getEmittedAt() > b.getRecord().getEmittedAt() ? a : b));
    // Filter expectedMessagesAfterSecondSync and keep latest messages only (keep same message order)
    final List<AirbyteMessage> expectedMessages = expectedMessagesAfterSecondSync
        .stream()
        .filter(message -> message.getType() == Type.RECORD && message.getRecord() != null)
        .filter(message -> {
          final String key = message.getRecord().getData().get("id").asText() +
              message.getRecord().getData().get("currency").asText() +
              message.getRecord().getData().get("date").asText() +
              message.getRecord().getData().get("NZD").asText();
          return message.getRecord().getEmittedAt().equals(latestMessagesOnly.get(key).getRecord().getEmittedAt());
        }).collect(Collectors.toList());

    final String defaultSchema = getDefaultSchema(config);
    retrieveRawRecordsAndAssertSameMessages(catalog, expectedMessagesAfterSecondSync, defaultSchema);
    final List<AirbyteRecordMessage> actualMessages = retrieveNormalizedRecords(catalog, defaultSchema);
    assertSameMessages(expectedMessages, actualMessages, true);
  }

  /**
   * This test is running a sync using the exchange rate catalog and messages. However it also
   * generates and adds two extra messages with big records (near the destination limit as defined by
   * getMaxValueLengthLimit()
   *
   * The first big message should be small enough to fit into the destination while the second message
   * would be too big and fails to replicate.
   */
  @Test
  void testSyncVeryBigRecords() throws Exception {
    if (!implementsRecordSizeLimitChecks()) {
      return;
    }

    final AirbyteCatalog catalog =
        Jsons.deserialize(MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.catalogFile), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.messageFile).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    // Add a big message that barely fits into the limits of the destination
    messages.add(new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(catalog.getStreams().get(0).getName())
            .withEmittedAt(Instant.now().toEpochMilli())
            .withData(Jsons.jsonNode(ImmutableMap.builder()
                .put("id", 3)
                // remove enough characters from max limit to fit the other columns and json characters
                .put("currency", generateBigString(-150))
                .put("date", "2020-10-10T00:00:00Z")
                .put("HKD", 10.5)
                .put("NZD", 1.14)
                .build()))));
    // Add a big message that does not fit into the limits of the destination
    final AirbyteMessage bigMessage = new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(catalog.getStreams().get(0).getName())
            .withEmittedAt(Instant.now().toEpochMilli())
            .withData(Jsons.jsonNode(ImmutableMap.builder()
                .put("id", 3)
                .put("currency", generateBigString(getGenerateBigStringAddExtraCharacters()))
                .put("date", "2020-10-10T00:00:00Z")
                .put("HKD", 10.5)
                .put("NZD", 1.14)
                .build())));
    final JsonNode config = getConfig();
    final String defaultSchema = getDefaultSchema(config);
    final List<AirbyteMessage> allMessages = new ArrayList<>();
    allMessages.add(bigMessage);
    allMessages.addAll(messages);
    runSyncAndVerifyStateOutput(config, allMessages, configuredCatalog, false);
    retrieveRawRecordsAndAssertSameMessages(catalog, messages, defaultSchema);
  }

  private String generateBigString(final int addExtraCharacters) {
    final int length = getMaxRecordValueLimit() + addExtraCharacters;
    return RANDOM
        .ints('a', 'z' + 1)
        .limit(length)
        .collect(StringBuilder::new, StringBuilder::appendCodePoint, StringBuilder::append)
        .toString();
  }

  protected int getGenerateBigStringAddExtraCharacters() {
    return 0;
  }

  /**
   * @return the max limit length allowed for values in the destination.
   */
  protected int getMaxRecordValueLimit() {
    return 1000000000;
  }

  @Test
  public void testCustomDbtTransformations() throws Exception {
    if (!dbtFromSpec()) {
      return;
    }

    final JsonNode config = getConfig();

    // This may throw IllegalStateException "Requesting normalization, but it is not included in the
    // normalization mappings"
    // We indeed require normalization implementation of the 'transform_config' function for this
    // destination,
    // because we make sure to install required dbt dependency in the normalization docker image in
    // order to run
    // this test successfully and that we are able to convert a destination 'config.json' into a dbt
    // 'profiles.yml'
    // (we don't actually rely on normalization running anything else here though)
    final DbtTransformationRunner runner = new DbtTransformationRunner(workerConfigs, processFactory, NormalizationRunnerFactory.create(
        workerConfigs,
        getImageName(),
        processFactory,
        NORMALIZATION_VERSION));
    runner.start();
    final Path transformationRoot = Files.createDirectories(jobRoot.resolve("transform"));
    final OperatorDbt dbtConfig = new OperatorDbt()
        // Forked from https://github.com/dbt-labs/jaffle_shop because they made a change that would have
        // required a dbt version upgrade
        // https://github.com/dbt-labs/jaffle_shop/commit/b1680f3278437c081c735b7ea71c2ff9707bc75f#diff-27386df54b2629c1191d8342d3725ed8678413cfa13b5556f59d69d33fae5425R20
        // We're actually two commits upstream of that, because the previous commit
        // (https://github.com/dbt-labs/jaffle_shop/commit/ec36ae177ab5cb79da39ff8ab068c878fbac13a0) also
        // breaks something
        // TODO once we're on DBT 1.x, switch this back to using the main branch
        .withGitRepoUrl("https://github.com/airbytehq/jaffle_shop.git")
        .withGitRepoBranch("pre_dbt_upgrade")
        .withDockerImage(NormalizationRunnerFactory.getNormalizationInfoForConnector(getImageName()).getLeft() + ":" + NORMALIZATION_VERSION);
    //
    // jaffle_shop is a fictional ecommerce store maintained by fishtownanalytics/dbt.
    //
    // This dbt project transforms raw data from an app database into a customers and orders model ready
    // for analytics.
    // The repo is a self-contained playground dbt project, useful for testing out scripts, and
    // communicating some of the core dbt concepts:
    //
    // 1. First, it tests if connection to the destination works.
    dbtConfig.withDbtArguments("debug");
    if (!runner.run(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
      throw new WorkerException("dbt debug Failed.");
    }
    // 2. Install any dependencies packages, if any
    dbtConfig.withDbtArguments("deps");
    if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
      throw new WorkerException("dbt deps Failed.");
    }
    // 3. It contains seeds that includes some (fake) raw data from a fictional app as CSVs data sets.
    // This materializes the CSVs as tables in your target schema.
    // Note that a typical dbt project does not require this step since dbt assumes your raw data is
    // already in your warehouse.
    dbtConfig.withDbtArguments("seed");
    if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
      throw new WorkerException("dbt seed Failed.");
    }
    // 4. Run the models:
    // Note: If this steps fails, it might mean that you need to make small changes to the SQL in the
    // models folder to adjust for the flavor of SQL of your target database.
    dbtConfig.withDbtArguments("run");
    if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
      throw new WorkerException("dbt run Failed.");
    }
    // 5. Test the output of the models and tables have been properly populated:
    dbtConfig.withDbtArguments("test");
    if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
      throw new WorkerException("dbt test Failed.");
    }
    // 6. Generate dbt documentation for the project:
    // This step is commented out because it takes a long time, but is not vital for Airbyte
    // dbtConfig.withDbtArguments("docs generate");
    // if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
    // throw new WorkerException("dbt docs generate Failed.");
    // }
    runner.close();
  }

  @Test
  void testCustomDbtTransformationsFailure() throws Exception {
    if (!normalizationFromSpec() || !dbtFromSpec()) {
      // we require normalization implementation for this destination, because we make sure to install
      // required dbt dependency in the normalization docker image in order to run this test successfully
      // (we don't actually rely on normalization running anything here though)
      return;
    }

    final JsonNode config = getConfig();

    final DbtTransformationRunner runner = new DbtTransformationRunner(workerConfigs, processFactory, NormalizationRunnerFactory.create(
        workerConfigs,
        getImageName(),
        processFactory,
        NORMALIZATION_VERSION));
    runner.start();
    final Path transformationRoot = Files.createDirectories(jobRoot.resolve("transform"));
    final OperatorDbt dbtConfig = new OperatorDbt()
        .withGitRepoUrl("https://github.com/fishtown-analytics/dbt-learn-demo.git")
        .withGitRepoBranch("main")
        .withDockerImage("fishtownanalytics/dbt:0.19.1")
        .withDbtArguments("debug");
    if (!runner.run(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
      throw new WorkerException("dbt debug Failed.");
    }

    dbtConfig.withDbtArguments("test");
    assertFalse(runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig),
        "dbt test should fail, as we haven't run dbt run on this project yet");
  }

  /**
   * Verify the destination uses the namespace field if it is set.
   */
  @Test
  void testSyncUsesAirbyteStreamNamespaceIfNotNull() throws Exception {
    if (!implementsNamespaces()) {
      return;
    }

    // TODO(davin): make these tests part of the catalog file.
    final AirbyteCatalog catalog =
        Jsons.deserialize(MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.catalogFile), AirbyteCatalog.class);
    final String namespace = "sourcenamespace";
    catalog.getStreams().forEach(stream -> stream.setNamespace(namespace));
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);

    final List<AirbyteMessage> messages = MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.messageFile).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    final List<AirbyteMessage> messagesWithNewNamespace = getRecordMessagesWithNewNamespace(messages, namespace);

    final JsonNode config = getConfig();
    final String defaultSchema = getDefaultSchema(config);
    runSyncAndVerifyStateOutput(config, messagesWithNewNamespace, configuredCatalog, false);
    retrieveRawRecordsAndAssertSameMessages(catalog, messagesWithNewNamespace, defaultSchema);
  }

  /**
   * Verify a destination is able to write tables with the same name to different namespaces.
   */
  @Test
  void testSyncWriteSameTableNameDifferentNamespace() throws Exception {
    if (!implementsNamespaces()) {
      return;
    }

    // TODO(davin): make these tests part of the catalog file.
    final var catalog =
        Jsons.deserialize(MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.catalogFile), AirbyteCatalog.class);
    final var namespace1 = "sourcenamespace";
    catalog.getStreams().forEach(stream -> stream.setNamespace(namespace1));

    final var diffNamespaceStreams = new ArrayList<AirbyteStream>();
    final var namespace2 = "diff_source_namespace";
    final var mapper = MoreMappers.initMapper();
    for (final AirbyteStream stream : catalog.getStreams()) {
      final var clonedStream = mapper.readValue(mapper.writeValueAsString(stream), AirbyteStream.class);
      clonedStream.setNamespace(namespace2);
      diffNamespaceStreams.add(clonedStream);
    }
    catalog.getStreams().addAll(diffNamespaceStreams);

    final var configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);

    final var ns1Messages = MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.messageFile).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    final var ns1MessagesAtNamespace1 = getRecordMessagesWithNewNamespace(ns1Messages, namespace1);
    final var ns2Messages = MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.messageFile).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    final var ns2MessagesAtNamespace2 = getRecordMessagesWithNewNamespace(ns2Messages, namespace2);

    final var allMessages = new ArrayList<>(ns1MessagesAtNamespace1);
    allMessages.addAll(ns2MessagesAtNamespace2);

    final JsonNode config = getConfig();
    final String defaultSchema = getDefaultSchema(config);
    runSyncAndVerifyStateOutput(config, allMessages, configuredCatalog, false);
    retrieveRawRecordsAndAssertSameMessages(catalog, allMessages, defaultSchema);
  }

  public static class NamespaceTestCaseProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) throws Exception {
      final JsonNode testCases =
          Jsons.deserialize(MoreResources.readResource("namespace_test_cases.json"));
      return MoreIterators.toList(testCases.elements()).stream()
          .filter(testCase -> testCase.get("enabled").asBoolean())
          .map(testCase -> Arguments.of(
              testCase.get("id").asText(),
              testCase.get("namespace").asText(),
              testCase.get("normalized").asText()));
    }

  }

  @ParameterizedTest
  @ArgumentsSource(NamespaceTestCaseProvider.class)
  public void testNamespaces(final String testCaseId, final String namespace, final String normalizedNamespace) throws Exception {
    final Optional<NamingConventionTransformer> nameTransformer = getNameTransformer();
    nameTransformer.ifPresent(namingConventionTransformer -> assertNamespaceNormalization(testCaseId, normalizedNamespace,
        namingConventionTransformer.getNamespace(namespace)));

    if (!implementsNamespaces() || !supportNamespaceTest()) {
      return;
    }

    final AirbyteCatalog catalog = Jsons.deserialize(
        MoreResources.readResource(DataArgumentsProvider.NAMESPACE_CONFIG.catalogFile), AirbyteCatalog.class);
    catalog.getStreams().forEach(stream -> stream.setNamespace(namespace));
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);

    final List<AirbyteMessage> messages = MoreResources.readResource(DataArgumentsProvider.NAMESPACE_CONFIG.messageFile).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    final List<AirbyteMessage> messagesWithNewNamespace = getRecordMessagesWithNewNamespace(messages, namespace);

    final JsonNode config = getConfig();
    try {
      runSyncAndVerifyStateOutput(config, messagesWithNewNamespace, configuredCatalog, false);
    } catch (final Exception e) {
      throw new IOException(String.format(
          "[Test Case %s] Destination failed to sync data to namespace %s, see \"namespace_test_cases.json for details\"",
          testCaseId, namespace), e);
    }
  }

  /**
   * In order to launch a source on Kubernetes in a pod, we need to be able to wrap the entrypoint.
   * The source connector must specify its entrypoint in the AIRBYTE_ENTRYPOINT variable. This test
   * ensures that the entrypoint environment variable is set.
   */
  @Test
  public void testEntrypointEnvVar() throws Exception {
    final String entrypoint = EntrypointEnvChecker.getEntrypointEnvVariable(
        processFactory,
        JOB_ID,
        JOB_ATTEMPT,
        jobRoot,
        getImageName());

    assertNotNull(entrypoint);
    assertFalse(entrypoint.isBlank());
  }

  /**
   * Verify that destination doesn't fail if new fields arrive in the data after initial schema
   * discovery and sync.
   *
   * @throws Exception
   */
  @Test
  public void testSyncNotFailsWithNewFields() throws Exception {
    if (!implementsOverwrite()) {
      LOGGER.info("Destination's spec.json does not support overwrite sync mode.");
      return;
    }

    final AirbyteCatalog catalog =
        Jsons.deserialize(MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.catalogFile), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);

    final List<AirbyteMessage> firstSyncMessages = MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.messageFile).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
    final JsonNode config = getConfig();
    runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredCatalog, false);
    final var stream = catalog.getStreams().get(0);

    // Run second sync with new fields on the message
    final List<AirbyteMessage> secondSyncMessagesWithNewFields = Lists.newArrayList(
        new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(stream.getName())
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.builder()
                    .put("id", 1)
                    .put("currency", "USD")
                    .put("date", "2020-03-31T00:00:00Z")
                    .put("newFieldString", "Value for new field")
                    .put("newFieldNumber", 3)
                    .put("HKD", 10.1)
                    .put("NZD", 700.1)
                    .build()))),
        new AirbyteMessage()
            .withType(Type.STATE)
            .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))));

    // Run sync and verify that all message were written without failing
    runSyncAndVerifyStateOutput(config, secondSyncMessagesWithNewFields, configuredCatalog, false);
    var destinationOutput = retrieveRecords(testEnv, stream.getName(), getDefaultSchema(config), stream.getJsonSchema());
    // Remove state message
    secondSyncMessagesWithNewFields.removeIf(airbyteMessage -> airbyteMessage.getType().equals(Type.STATE));
    assertEquals(secondSyncMessagesWithNewFields.size(), destinationOutput.size());
  }

  /**
   * Whether the destination should be tested against different namespaces.
   */
  protected boolean supportNamespaceTest() {
    return false;
  }

  /**
   * Set up the name transformer used by a destination to test it against a variety of namespaces.
   */
  protected Optional<NamingConventionTransformer> getNameTransformer() {
    return Optional.empty();
  }

  /**
   * Override this method if the normalized namespace is different from the default one. E.g. BigQuery
   * does allow a name starting with a number. So it should change the expected normalized namespace
   * when testCaseId = "S3A-1". Find the testCaseId in "namespace_test_cases.json".
   */
  protected void assertNamespaceNormalization(final String testCaseId,
                                              final String expectedNormalizedNamespace,
                                              final String actualNormalizedNamespace) {
    assertEquals(expectedNormalizedNamespace, actualNormalizedNamespace,
        String.format("Test case %s failed; if this is expected, please override assertNamespaceNormalization", testCaseId));
  }

  private ConnectorSpecification runSpec() throws WorkerException {
    return new DefaultGetSpecWorker(
        workerConfigs, new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, null))
            .run(new JobGetSpecConfig().withDockerImage(getImageName()), jobRoot).getSpec();
  }

  protected StandardCheckConnectionOutput runCheck(final JsonNode config) throws WorkerException {
    return new DefaultCheckConnectionWorker(
        workerConfigs, new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, null))
            .run(new StandardCheckConnectionInput().withConnectionConfiguration(config), jobRoot).getCheckConnection();
  }

  protected StandardCheckConnectionOutput.Status runCheckWithCatchedException(final JsonNode config) {
    try {
      final StandardCheckConnectionOutput standardCheckConnectionOutput = new DefaultCheckConnectionWorker(
          workerConfigs, new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, null))
              .run(new StandardCheckConnectionInput().withConnectionConfiguration(config), jobRoot).getCheckConnection();
      return standardCheckConnectionOutput.getStatus();
    } catch (final Exception e) {
      LOGGER.error("Failed to check connection:" + e.getMessage());
    }
    return Status.FAILED;
  }

  protected AirbyteDestination getDestination() {
    return new DefaultAirbyteDestination(
        workerConfigs, new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory, null));
  }

  protected void runSyncAndVerifyStateOutput(final JsonNode config,
                                             final List<AirbyteMessage> messages,
                                             final ConfiguredAirbyteCatalog catalog,
                                             final boolean runNormalization)
      throws Exception {
    final List<AirbyteMessage> destinationOutput = runSync(config, messages, catalog, runNormalization);
    final AirbyteMessage expectedStateMessage = MoreLists.reversed(messages)
        .stream()
        .filter(m -> m.getType() == Type.STATE)
        .findFirst()
        .orElseThrow(() -> new IllegalArgumentException("All message sets used for testing should include a state record"));

    final AirbyteMessage actualStateMessage = MoreLists.reversed(destinationOutput)
        .stream()
        .filter(m -> m.getType() == Type.STATE)
        .findFirst()
        .orElseGet(() -> {
          fail("Destination failed to output state");
          return null;
        });

    assertEquals(expectedStateMessage, actualStateMessage);
  }

  private List<AirbyteMessage> runSync(
                                       final JsonNode config,
                                       final List<AirbyteMessage> messages,
                                       final ConfiguredAirbyteCatalog catalog,
                                       final boolean runNormalization)
      throws Exception {

    final WorkerDestinationConfig destinationConfig = new WorkerDestinationConfig()
        .withConnectionId(UUID.randomUUID())
        .withCatalog(catalog)
        .withDestinationConnectionConfiguration(config);

    final AirbyteDestination destination = getDestination();

    destination.start(destinationConfig, jobRoot);
    messages.forEach(message -> Exceptions.toRuntime(() -> destination.accept(message)));
    destination.notifyEndOfInput();

    final List<AirbyteMessage> destinationOutput = new ArrayList<>();
    while (!destination.isFinished()) {
      destination.attemptRead().ifPresent(destinationOutput::add);
    }

    destination.close();

    if (!runNormalization) {
      return destinationOutput;
    }

    final NormalizationRunner runner = NormalizationRunnerFactory.create(
        workerConfigs,
        getImageName(),
        processFactory,
        NORMALIZATION_VERSION);
    runner.start();
    final Path normalizationRoot = Files.createDirectories(jobRoot.resolve("normalize"));
    if (!runner.normalize(JOB_ID, JOB_ATTEMPT, normalizationRoot, destinationConfig.getDestinationConnectionConfiguration(),
        destinationConfig.getCatalog(), null)) {
      throw new WorkerException("Normalization Failed.");
    }
    runner.close();
    return destinationOutput;
  }

  protected void retrieveRawRecordsAndAssertSameMessages(final AirbyteCatalog catalog,
                                                         final List<AirbyteMessage> messages,
                                                         final String defaultSchema)
      throws Exception {
    final List<AirbyteRecordMessage> actualMessages = new ArrayList<>();
    for (final AirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getName();
      final String schema = stream.getNamespace() != null ? stream.getNamespace() : defaultSchema;
      final List<AirbyteRecordMessage> msgList = retrieveRecords(testEnv, streamName, schema, stream.getJsonSchema())
          .stream()
          .map(data -> new AirbyteRecordMessage().withStream(streamName).withNamespace(schema).withData(data)).toList();
      actualMessages.addAll(msgList);
    }

    assertSameMessages(messages, actualMessages, false);
  }

  // ignores emitted at.
  protected void assertSameMessages(final List<AirbyteMessage> expected,
                                    final List<AirbyteRecordMessage> actual,
                                    final boolean pruneAirbyteInternalFields) {
    final List<JsonNode> expectedProcessed = expected.stream()
        .filter(message -> message.getType() == AirbyteMessage.Type.RECORD)
        .map(AirbyteMessage::getRecord)
        .peek(recordMessage -> recordMessage.setEmittedAt(null))
        .map(recordMessage -> pruneAirbyteInternalFields ? safePrune(recordMessage) : recordMessage)
        .map(AirbyteRecordMessage::getData)
        .collect(Collectors.toList());

    final List<JsonNode> actualProcessed = actual.stream()
        .map(recordMessage -> pruneAirbyteInternalFields ? safePrune(recordMessage) : recordMessage)
        .map(AirbyteRecordMessage::getData)
        .collect(Collectors.toList());

    testDataComparator.assertSameData(expectedProcessed, actualProcessed);
  }

  protected List<AirbyteRecordMessage> retrieveNormalizedRecords(final AirbyteCatalog catalog, final String defaultSchema) throws Exception {
    final List<AirbyteRecordMessage> actualMessages = new ArrayList<>();

    for (final AirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getName();

      final List<AirbyteRecordMessage> msgList = retrieveNormalizedRecords(testEnv, streamName, defaultSchema)
          .stream()
          .map(data -> new AirbyteRecordMessage().withStream(streamName).withData(data)).toList();
      actualMessages.addAll(msgList);
    }
    return actualMessages;
  }

  /**
   * Same as {@link #pruneMutate(JsonNode)}, except does a defensive copy and returns a new json node
   * object instead of mutating in place.
   *
   * @param record - record that will be pruned.
   * @return pruned json node.
   */
  private AirbyteRecordMessage safePrune(final AirbyteRecordMessage record) {
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
  private void pruneMutate(final JsonNode json) {
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
          "HASHID",
          "unique_key",
          "UNIQUE_KEY");
      if (airbyteInternalFields.stream().anyMatch(internalField -> key.toLowerCase().contains(internalField.toLowerCase()))
          || json.get(key).isNull()) {
        ((ObjectNode) json).remove(key);
      }
    }
  }

  public static class TestDestinationEnv {

    private final Path localRoot;

    public TestDestinationEnv(final Path localRoot) {
      this.localRoot = localRoot;
    }

    public Path getLocalRoot() {
      return localRoot;
    }

    @Override
    public String toString() {
      return "TestDestinationEnv{" +
          "localRoot=" + localRoot +
          '}';
    }

  }

  /**
   * This test MUST be disabled by default, but you may uncomment it and use when need to reproduce a
   * performance issue for destination. This test helps you to emulate lot's of stream and messages in
   * each simply changing the "streamsSize" args to set a number of tables\streams and the
   * "messagesNumber" to a messages number that would be written in each stream. !!! Do NOT forget to
   * manually remove all generated objects !!! Hint: To check the destination container output run
   * "docker ps" command in console to find the container's id. Then run "docker container attach
   * your_containers_id" (ex. docker container attach 18cc929f44c8) to see the container's output
   */
  @Test
  @Disabled
  public void testStressPerformance() throws Exception {
    final int streamsSize = 5; // number of generated streams
    final int messagesNumber = 300; // number of msg to be written to each generated stream

    // Each stream will have an id and name fields
    final String USERS_STREAM_NAME = "users"; // stream's name prefix. Will get "user0", "user1", etc.
    final String ID = "id";
    final String NAME = "name";

    // generate schema\catalogs
    final List<AirbyteStream> configuredAirbyteStreams = new ArrayList<>();
    for (int i = 0; i < streamsSize; i++) {
      configuredAirbyteStreams
          .add(CatalogHelpers.createAirbyteStream(USERS_STREAM_NAME + i,
              Field.of(NAME, JsonSchemaType.STRING),
              Field
                  .of(ID, JsonSchemaType.STRING)));
    }
    final AirbyteCatalog testCatalog = new AirbyteCatalog().withStreams(configuredAirbyteStreams);
    final ConfiguredAirbyteCatalog configuredTestCatalog = CatalogHelpers
        .toDefaultConfiguredCatalog(testCatalog);

    final JsonNode config = getConfig();
    final WorkerDestinationConfig destinationConfig = new WorkerDestinationConfig()
        .withConnectionId(UUID.randomUUID())
        .withCatalog(configuredTestCatalog)
        .withDestinationConnectionConfiguration(config);
    final AirbyteDestination destination = getDestination();

    // Start destination
    destination.start(destinationConfig, jobRoot);

    final AtomicInteger currentStreamNumber = new AtomicInteger(0);
    final AtomicInteger currentRecordNumberForStream = new AtomicInteger(0);

    // this is just a current state logger. Useful when running long hours tests to see the progress
    final Thread countPrinter = new Thread(() -> {
      while (true) {
        System.out.println(
            "currentStreamNumber=" + currentStreamNumber + ", currentRecordNumberForStream="
                + currentRecordNumberForStream + ", " + DateTime.now());
        try {
          Thread.sleep(10000);
        } catch (final InterruptedException e) {
          e.printStackTrace();
        }
      }

    });
    countPrinter.start();

    // iterate through streams
    for (int streamCounter = 0; streamCounter < streamsSize; streamCounter++) {
      LOGGER.info("Started new stream processing with #" + streamCounter);
      // iterate through msm inside a particular stream
      // Generate messages and put it to stream
      for (int msgCounter = 0; msgCounter < messagesNumber; msgCounter++) {
        final AirbyteMessage msg = new AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME + streamCounter)
                .withData(
                    Jsons.jsonNode(
                        ImmutableMap.builder().put(NAME, LOREM_IPSUM)
                            .put(ID, streamCounter + "_" + msgCounter)
                            .build()))
                .withEmittedAt(Instant.now().toEpochMilli()));
        try {
          destination.accept(msg);
        } catch (final Exception e) {
          LOGGER.error("Failed to write a RECORD message: " + e);
          throw new RuntimeException(e);
        }

        currentRecordNumberForStream.set(msgCounter);
      }

      // send state message here, it's required
      final AirbyteMessage msgState = new AirbyteMessage()
          .withType(AirbyteMessage.Type.STATE)
          .withState(new AirbyteStateMessage()
              .withData(
                  Jsons.jsonNode(ImmutableMap.builder().put("start_date", "2020-09-02").build())));
      try {
        destination.accept(msgState);
      } catch (final Exception e) {
        LOGGER.error("Failed to write a STATE message: " + e);
        throw new RuntimeException(e);
      }

      currentStreamNumber.set(streamCounter);
    }

    LOGGER.info(String
        .format("Added %s messages to each of %s streams", currentRecordNumberForStream,
            currentStreamNumber));
    // Close destination
    destination.notifyEndOfInput();
  }

  private final static String LOREM_IPSUM =
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque malesuada lacinia aliquet. Nam feugiat mauris vel magna dignissim feugiat. Nam non dapibus sapien, ac mattis purus. Donec mollis libero erat, a rutrum ipsum pretium id. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Integer nec aliquam leo. Aliquam eu dictum augue, a ornare elit.\n"
          + "\n"
          + "Nulla viverra blandit neque. Nam blandit varius efficitur. Nunc at sapien blandit, malesuada lectus vel, tincidunt orci. Proin blandit metus eget libero facilisis interdum. Aenean luctus scelerisque orci, at scelerisque sem vestibulum in. Nullam ornare massa sed dui efficitur, eget volutpat lectus elementum. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Integer elementum mi vitae erat eleifend iaculis. Nullam eget tincidunt est, eget tempor est. Sed risus velit, iaculis vitae est in, volutpat consectetur odio. Aenean ut fringilla elit. Suspendisse non aliquet massa. Curabitur suscipit metus nunc, nec porttitor velit venenatis vel. Fusce vestibulum eleifend diam, lobortis auctor magna.\n"
          + "\n"
          + "Etiam maximus, mi feugiat pharetra mattis, nulla neque euismod metus, in congue nunc sem nec ligula. Curabitur aliquam, risus id convallis cursus, nunc orci sollicitudin enim, quis scelerisque nibh dui in ipsum. Suspendisse mollis, metus a dapibus scelerisque, sapien nulla pretium ipsum, non finibus sem orci et lectus. Aliquam dictum magna nisi, a consectetur urna euismod nec. In pulvinar facilisis nulla, id mollis libero pulvinar vel. Nam a commodo leo, eu commodo dolor. In hac habitasse platea dictumst. Curabitur auctor purus quis tortor laoreet efficitur. Quisque tincidunt, risus vel rutrum fermentum, libero urna dignissim augue, eget pulvinar nibh ligula ut tortor. Vivamus convallis non risus sed consectetur. Etiam accumsan enim ac nisl suscipit, vel congue lorem volutpat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce non orci quis lacus rhoncus vestibulum nec ut magna. In varius lectus nec quam posuere finibus. Vivamus quis lectus vitae tortor sollicitudin fermentum.\n"
          + "\n"
          + "Pellentesque elementum vehicula egestas. Sed volutpat velit arcu, at imperdiet sapien consectetur facilisis. Suspendisse porttitor tincidunt interdum. Morbi gravida faucibus tortor, ut rutrum magna tincidunt a. Morbi eu nisi eget dui finibus hendrerit sit amet in augue. Aenean imperdiet lacus enim, a volutpat nulla placerat at. Suspendisse nibh ipsum, venenatis vel maximus ut, fringilla nec felis. Sed risus mi, egestas quis quam ullamcorper, pharetra vestibulum diam.\n"
          + "\n"
          + "Praesent finibus scelerisque elit, accumsan condimentum risus mattis vitae. Donec tristique hendrerit facilisis. Curabitur metus purus, venenatis non elementum id, finibus eu augue. Quisque posuere rhoncus ligula, et vehicula erat pulvinar at. Pellentesque vel quam vel lectus tincidunt congue quis id sapien. Ut efficitur mauris vitae pretium iaculis. Aliquam consectetur iaculis nisi vitae laoreet. Integer vel odio quis diam mattis tempor eget nec est. Donec iaculis facilisis neque, at dictum magna vestibulum ut. Sed malesuada non nunc ac consequat. Maecenas tempus lectus a nisl congue, ac venenatis diam viverra. Nam ac justo id nulla iaculis lobortis in eu ligula. Vivamus et ligula id sapien efficitur aliquet. Curabitur est justo, tempus vitae mollis quis, tincidunt vitae felis. Vestibulum molestie laoreet justo, nec mollis purus vulputate at.";

  protected TestDataComparator getTestDataComparator() {
    return new BasicTestDataComparator(this::resolveIdentifier);
  }

  protected boolean supportBasicDataTypeTest() {
    return false;
  }

  protected boolean supportArrayDataTypeTest() {
    return false;
  }

  protected boolean supportObjectDataTypeTest() {
    return false;
  }

  private boolean checkTestCompatibility(final DataTypeTestArgumentProvider.TestCompatibility testCompatibility) {
    return testCompatibility.isTestCompatible(supportBasicDataTypeTest(), supportArrayDataTypeTest(), supportObjectDataTypeTest());
  }

  @ParameterizedTest
  @ArgumentsSource(DataTypeTestArgumentProvider.class)
  public void testDataTypeTestWithNormalization(final String messagesFilename,
                                                final String catalogFilename,
                                                final DataTypeTestArgumentProvider.TestCompatibility testCompatibility)
      throws Exception {
    if (!checkTestCompatibility(testCompatibility))
      return;

    final AirbyteCatalog catalog = readCatalogFromFile(catalogFilename);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = readMessagesFromFile(messagesFilename);

    if (supportsNormalization()) {
      LOGGER.info("Normalization is supported! Run test with normalization.");
      runAndCheckWithNormalization(messages, configuredCatalog, catalog);
    } else {
      LOGGER.info("Normalization is not supported! Run test without normalization.");
      runAndCheckWithoutNormalization(messages, configuredCatalog, catalog);
    }
  }

  private AirbyteCatalog readCatalogFromFile(final String catalogFilename) throws IOException {
    return Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
  }

  private List<AirbyteMessage> readMessagesFromFile(final String messagesFilename) throws IOException {
    return MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
  }

  private void runAndCheckWithNormalization(final List<AirbyteMessage> messages,
                                            final ConfiguredAirbyteCatalog configuredCatalog,
                                            final AirbyteCatalog catalog)
      throws Exception {
    final JsonNode config = getConfig();
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true);

    final List<AirbyteRecordMessage> actualMessages = retrieveNormalizedRecords(catalog, getDefaultSchema(config));
    assertSameMessages(messages, actualMessages, true);
  }

  private void runAndCheckWithoutNormalization(final List<AirbyteMessage> messages,
                                               final ConfiguredAirbyteCatalog configuredCatalog,
                                               final AirbyteCatalog catalog)
      throws Exception {
    final JsonNode config = getConfig();
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false);
    retrieveRawRecordsAndAssertSameMessages(catalog, messages, getDefaultSchema(config));
  }

  /**
   * Mutate the input airbyte record message namespace.
   */
  private static List<AirbyteMessage> getRecordMessagesWithNewNamespace(final List<AirbyteMessage> airbyteMessages, final String namespace) {
    airbyteMessages.forEach(message -> {
      if (message.getRecord() != null) {
        message.getRecord().setNamespace(namespace);
      }
    });
    return airbyteMessages;
  }

}
