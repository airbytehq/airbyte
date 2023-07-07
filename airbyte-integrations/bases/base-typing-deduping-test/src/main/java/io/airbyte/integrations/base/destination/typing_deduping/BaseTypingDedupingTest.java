/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.configoss.WorkerDestinationConfig;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import io.airbyte.workers.internal.AirbyteDestination;
import io.airbyte.workers.internal.DefaultAirbyteDestination;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.stream.Stream;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This is loosely based on standard-destination-tests's DestinationAcceptanceTest class. The
 * sync-running code is copy-pasted from there.
 * <p>
 * All tests use a single stream, whose schema is defined in {@code resources/schema.json}. Each
 * test case constructs a ConfiguredAirbyteCatalog dynamically.
 * <p>
 * For sync modes which use a primary key, the stream provides a composite key of (id1, id2). For
 * sync modes which use a cursor, the stream provides an updated_at field. The stream also has an
 * _ab_cdc_deleted_at field.
 */
// If you're running from inside intellij, you must run your specific subclass to get concurrent
// execution.
@Execution(ExecutionMode.CONCURRENT)
public abstract class BaseTypingDedupingTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseTypingDedupingTest.class);
  private static final JsonNode SCHEMA;
  static {
    try {
      SCHEMA = Jsons.deserialize(MoreResources.readResource("schema.json"));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }
  private static final RecordDiffer DIFFER = new RecordDiffer(
      Pair.of("id1", AirbyteProtocolType.INTEGER),
      Pair.of("id2", AirbyteProtocolType.INTEGER),
      Pair.of("updated_at", AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE));

  private String randomSuffix;
  private JsonNode config;
  private String streamNamespace;
  private String streamName;
  private List<AirbyteStreamNameNamespacePair> streamsToTearDown;

  /**
   * @return the docker image to run, e.g. {@code "airbyte/destination-bigquery:dev"}.
   */
  protected abstract String getImageName();

  /**
   * Get the destination connector config. Subclasses may use this method for other setup work, e.g.
   * opening a connection to the destination.
   * <p>
   * Subclasses should _not_ start testcontainers in this method; that belongs in a BeforeAll method.
   * The tests in this class are intended to be run concurrently on a shared database and will not
   * interfere with each other.
   * <p>
   * Sublcasses which need access to the config may use {@link #getConfig()}.
   */
  protected abstract JsonNode generateConfig() throws Exception;

  /**
   * For a given stream, return the records that exist in the destination's raw table. Each record
   * must be in the format {"_airbyte_raw_id": "...", "_airbyte_extracted_at": "...",
   * "_airbyte_loaded_at": "...", "_airbyte_data": {fields...}}.
   * <p>
   * The {@code _airbyte_data} column must be an
   * {@link com.fasterxml.jackson.databind.node.ObjectNode} (i.e. it cannot be a string value).
   * <p>
   * streamNamespace may be null, in which case you should query from the default namespace.
   */
  protected abstract List<JsonNode> dumpRawTableRecords(String streamNamespace, String streamName) throws Exception;

  /**
   * For a given stream, return the records that exist in the destination's final table. Each record
   * must be in the format {"_airbyte_raw_id": "...", "_airbyte_extracted_at": "...", "_airbyte_meta":
   * {...}, "field1": ..., "field2": ..., ...}.
   * <p>
   * For JSON-valued columns, there is some nuance: a SQL null should be represented as a missing
   * entry, whereas a JSON null should be represented as a
   * {@link com.fasterxml.jackson.databind.node.NullNode}. For example, in the JSON blob {"name":
   * null}, the `name` field is a JSON null, and the `address` field is a SQL null.
   * <p>
   * The corresponding SQL looks like
   * {@code INSERT INTO ... (name, address) VALUES ('null' :: jsonb, NULL)}.
   * <p>
   * streamNamespace may be null, in which case you should query from the default namespace.
   */
  protected abstract List<JsonNode> dumpFinalTableRecords(String streamNamespace, String streamName) throws Exception;

  /**
   * Delete any resources in the destination associated with this stream AND its namespace. We need
   * this because we write raw tables to a shared {@code airbyte} namespace, which we can't drop
   * wholesale. Must handle the case where the table/namespace doesn't exist (e.g. if the connector
   * crashed without writing any data).
   * <p>
   * In general, this should resemble
   * {@code DROP TABLE IF EXISTS airbyte.<streamNamespace>_<streamName>; DROP SCHEMA IF EXISTS <streamNamespace>}.
   */
  protected abstract void teardownStreamAndNamespace(String streamNamespace, String streamName) throws Exception;

  /**
   * @return A suffix which is different for each concurrent test run.
   */
  protected synchronized String getUniqueSuffix() {
    if (randomSuffix == null) {
      randomSuffix = "_" + RandomStringUtils.randomAlphabetic(5).toLowerCase();
    }
    return randomSuffix;
  }

  protected JsonNode getConfig() {
    return config;
  }

  @BeforeEach
  public void setup() throws Exception {
    config = generateConfig();
    streamNamespace = "typing_deduping_test" + getUniqueSuffix();
    streamName = "test_stream" + getUniqueSuffix();
    streamsToTearDown = new ArrayList<>();
    LOGGER.info("Using stream namespace {} and name {}", streamNamespace, streamName);
  }

  @AfterEach
  public void teardown() throws Exception {
    for (AirbyteStreamNameNamespacePair streamId : streamsToTearDown) {
      teardownStreamAndNamespace(streamId.getNamespace(), streamId.getName());
    }
  }

  /**
   * Starting with an empty destination, execute a full refresh overwrite sync. Verify that the
   * records are written to the destination table. Then run a second sync, and verify that the records
   * are overwritten.
   */
  @Test
  public void fullRefreshOverwrite() throws Exception {
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    // First sync
    List<AirbyteMessage> messages1 = readMessages("sync1_messages.jsonl");

    runSync(catalog, messages1);

    List<JsonNode> expectedRawRecords1 = readRecords("sync1_expectedrecords_nondedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords1 = readRecords("sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1);

    // Second sync
    List<AirbyteMessage> messages2 = readMessages("sync2_messages.jsonl");

    runSync(catalog, messages2);

    List<JsonNode> expectedRawRecords2 = readRecords("sync2_expectedrecords_fullrefresh_overwrite_raw.jsonl");
    List<JsonNode> expectedFinalRecords2 = readRecords("sync2_expectedrecords_fullrefresh_overwrite_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2);
  }

  /**
   * Starting with an empty destination, execute a full refresh append sync. Verify that the records
   * are written to the destination table. Then run a second sync, and verify that the old and new
   * records are all present.
   */
  @Test
  public void fullRefreshAppend() throws Exception {
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    // First sync
    List<AirbyteMessage> messages1 = readMessages("sync1_messages.jsonl");

    runSync(catalog, messages1);

    List<JsonNode> expectedRawRecords1 = readRecords("sync1_expectedrecords_nondedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords1 = readRecords("sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1);

    // Second sync
    List<AirbyteMessage> messages2 = readMessages("sync2_messages.jsonl");

    runSync(catalog, messages2);

    List<JsonNode> expectedRawRecords2 = readRecords("sync2_expectedrecords_fullrefresh_append_raw.jsonl");
    List<JsonNode> expectedFinalRecords2 = readRecords("sync2_expectedrecords_fullrefresh_append_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2);
  }

  /**
   * Starting with an empty destination, execute an incremental append sync.
   * <p>
   * This is (not so secretly) identical to {@link #fullRefreshAppend()}, and uses the same set of
   * expected records. Incremental as a concept only exists in the source. From the destination's
   * perspective, we only care about the destination sync mode.
   */
  @Test
  public void incrementalAppend() throws Exception {
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            // These two lines are literally the only difference between this test and fullRefreshAppend
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    // First sync
    List<AirbyteMessage> messages1 = readMessages("sync1_messages.jsonl");

    runSync(catalog, messages1);

    List<JsonNode> expectedRawRecords1 = readRecords("sync1_expectedrecords_nondedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords1 = readRecords("sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1);

    // Second sync
    List<AirbyteMessage> messages2 = readMessages("sync2_messages.jsonl");

    runSync(catalog, messages2);

    List<JsonNode> expectedRawRecords2 = readRecords("sync2_expectedrecords_fullrefresh_append_raw.jsonl");
    List<JsonNode> expectedFinalRecords2 = readRecords("sync2_expectedrecords_fullrefresh_append_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2);
  }

  /**
   * Starting with an empty destination, execute an incremental dedup sync. Verify that the records
   * are written to the destination table. Then run a second sync, and verify that the raw/final
   * tables contain the correct records.
   */
  @Test
  public void incrementalDedup() throws Exception {
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    // First sync
    List<AirbyteMessage> messages1 = readMessages("sync1_messages.jsonl");

    runSync(catalog, messages1);

    List<JsonNode> expectedRawRecords1 = readRecords("sync1_expectedrecords_dedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords1 = readRecords("sync1_expectedrecords_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1);

    // Second sync
    List<AirbyteMessage> messages2 = readMessages("sync2_messages.jsonl");

    runSync(catalog, messages2);

    List<JsonNode> expectedRawRecords2 = readRecords("sync2_expectedrecords_incremental_dedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords2 = readRecords("sync2_expectedrecords_incremental_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2);
  }

  /**
   * Identical to {@link #incrementalDedup()}, except that the stream has no namespace.
   */
  @Test
  public void incrementalDedupDefaultNamespace() throws Exception {
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                // NB: we don't call `withNamespace` here
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    // First sync
    List<AirbyteMessage> messages1 = readMessages("sync1_messages.jsonl", null, streamName);

    runSync(catalog, messages1);

    List<JsonNode> expectedRawRecords1 = readRecords("sync1_expectedrecords_dedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords1 = readRecords("sync1_expectedrecords_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, null, streamName);

    // Second sync
    List<AirbyteMessage> messages2 = readMessages("sync2_messages.jsonl", null, streamName);

    runSync(catalog, messages2);

    List<JsonNode> expectedRawRecords2 = readRecords("sync2_expectedrecords_incremental_dedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords2 = readRecords("sync2_expectedrecords_incremental_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, null, streamName);
  }

  @Test
  @Disabled("Not yet implemented")
  public void testLineBreakCharacters() throws Exception {
    // TODO verify that we can handle strings with interesting characters
    // build an airbyterecordmessage using something like this, and add it to the input messages:
    Jsons.jsonNode(ImmutableMap.builder()
        .put("id", 1)
        .put("currency", "USD\u2028")
        .put("date", "2020-03-\n31T00:00:00Z\r")
        // TODO(sherifnada) hack: write decimals with sigfigs because Snowflake stores 10.1 as "10" which
        // fails destination tests
        .put("HKD", 10.1)
        .put("NZD", 700.1)
        .build());
  }

  @Test
  @Disabled("Not yet implemented")
  public void testIncrementalSyncDropOneColumn() throws Exception {
    // TODO in incremental dedup mode: run a sync, remove a column from the schema, run another sync
    // verify that the column is dropped from the destination table
  }

  @Test
  @Disabled("Not yet implemented")
  public void testSyncUsesAirbyteStreamNamespaceIfNotNull() throws Exception {
    // TODO duplicate this test for each sync mode. Run 1st+2nd syncs using a stream with null
    // namespace:
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(null)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));
  }

  // TODO duplicate this test for each sync mode. Run 1st+2nd syncs using two streams with the same
  // name but different namespace
  // TODO maybe we don't even need the single-stream versions...
  /**
   * Identical to {@link #incrementalDedup()}, except there are two streams with the same name and
   * different namespace.
   */
  @Test
  public void incrementalDedupIdenticalName() throws Exception {
    String namespace1 = streamNamespace + "_1";
    String namespace2 = streamNamespace + "_2";
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(namespace1)
                .withName(streamName)
                .withJsonSchema(SCHEMA)),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(namespace2)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    // First sync
    // Read the same set of messages for both streams
    List<AirbyteMessage> messages1 = Stream.concat(
        readMessages("sync1_messages.jsonl", namespace1, streamName).stream(),
        readMessages("sync1_messages.jsonl", namespace2, streamName).stream()).toList();

    runSync(catalog, messages1);

    List<JsonNode> expectedRawRecords1 = readRecords("sync1_expectedrecords_dedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords1 = readRecords("sync1_expectedrecords_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, namespace1, streamName);
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, namespace2, streamName);

    // Second sync
    List<AirbyteMessage> messages2 = Stream.concat(
        readMessages("sync2_messages.jsonl", namespace1, streamName).stream(),
        readMessages("sync2_messages.jsonl", namespace2, streamName).stream()).toList();

    runSync(catalog, messages2);

    List<JsonNode> expectedRawRecords2 = readRecords("sync2_expectedrecords_incremental_dedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords2 = readRecords("sync2_expectedrecords_incremental_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, namespace1, streamName);
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, namespace2, streamName);
  }

  @Test
  @Disabled("Not yet implemented")
  public void testSyncNotFailsWithNewFields() throws Exception {
    // TODO duplicate this test for each sync mode. Run a sync, then add a new field to the schema, then
    // run another sync
    // We might want to write a test that verifies more general schema evolution (e.g. all valid
    // evolutions)
  }

  @Test
  @Disabled("Not yet implemented")
  public void testSyncWithLargeRecordBatch() throws Exception {
    // TODO duplicate this test for each sync mode. Run a single sync with many records
    /*
     * copied from DATs: This serves to test MSSQL 2100 limit parameters in a single query. this means
     * that for Airbyte insert data need to limit to ~ 700 records (3 columns for the raw tables) = 2100
     * params
     *
     * this maybe needs configuration per destination to specify that limit?
     */
  }

  @Test
  @Disabled("Not yet implemented")
  public void testDataTypes() throws Exception {
    // TODO duplicate this test for each sync mode. See DataTypeTestArgumentProvider for what this test
    // does in DAT-land
    // we probably don't want to do the exact same thing, but the general spirit of testing a wide range
    // of values for every data type is approximately correct
    // this test probably needs some configuration per destination to specify what values are supported?
  }

  private void verifySyncResult(List<JsonNode> expectedRawRecords, List<JsonNode> expectedFinalRecords) throws Exception {
    verifySyncResult(expectedRawRecords, expectedFinalRecords, streamNamespace, streamName);
  }

  private void verifySyncResult(List<JsonNode> expectedRawRecords,
                                List<JsonNode> expectedFinalRecords,
                                String streamNamespace,
                                String streamName)
      throws Exception {
    List<JsonNode> actualRawRecords = dumpRawTableRecords(streamNamespace, streamName);
    List<JsonNode> actualFinalRecords = dumpFinalTableRecords(streamNamespace, streamName);
    DIFFER.verifySyncResult(expectedRawRecords, actualRawRecords, expectedFinalRecords, actualFinalRecords);
  }

  private static List<JsonNode> readRecords(String filename) throws IOException {
    return MoreResources.readResource(filename).lines()
        .map(String::trim)
        .filter(line -> !line.isEmpty())
        .filter(line -> !line.startsWith("//"))
        .map(Jsons::deserialize)
        .toList();
  }

  private List<AirbyteMessage> readMessages(String filename) throws IOException {
    return readMessages(filename, streamNamespace, streamName);
  }

  private static List<AirbyteMessage> readMessages(String filename, String streamNamespace, String streamName) throws IOException {
    return readRecords(filename).stream()
        .map(record -> Jsons.convertValue(record, AirbyteMessage.class))
        .peek(message -> {
          message.getRecord().setNamespace(streamNamespace);
          message.getRecord().setStream(streamName);
        }).toList();
  }

  /*
   * !!!!!! WARNING !!!!!! The code below was mostly copypasted from DestinationAcceptanceTest. If you
   * make edits here, you probably want to also edit there.
   */

  // These contain some state, so they are instanced per test (i.e. cannot be static)
  private Path jobRoot;
  private ProcessFactory processFactory;

  @BeforeEach
  public void setupProcessFactory() throws IOException {
    final Path testDir = Path.of("/tmp/airbyte_tests/");
    Files.createDirectories(testDir);
    final Path workspaceRoot = Files.createTempDirectory(testDir, "test");
    jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"));
    Path localRoot = Files.createTempDirectory(testDir, "output");
    processFactory = new DockerProcessFactory(
        workspaceRoot,
        workspaceRoot.toString(),
        localRoot.toString(),
        "host",
        Collections.emptyMap());
  }

  private void runSync(ConfiguredAirbyteCatalog catalog, List<AirbyteMessage> messages) throws Exception {
    catalog.getStreams().forEach(s -> streamsToTearDown.add(AirbyteStreamNameNamespacePair.fromAirbyteStream(s.getStream())));

    final WorkerDestinationConfig destinationConfig = new WorkerDestinationConfig()
        .withConnectionId(UUID.randomUUID())
        .withCatalog(convertProtocolObject(catalog, io.airbyte.protocol.models.ConfiguredAirbyteCatalog.class))
        .withDestinationConnectionConfiguration(config);

    final AirbyteDestination destination = new DefaultAirbyteDestination(new AirbyteIntegrationLauncher(
        "0",
        0,
        getImageName(),
        processFactory,
        null,
        null,
        false,
        new EnvVariableFeatureFlags()));

    destination.start(destinationConfig, jobRoot, Collections.emptyMap());
    messages.forEach(
        message -> Exceptions.toRuntime(() -> destination.accept(convertProtocolObject(message, io.airbyte.protocol.models.AirbyteMessage.class))));
    destination.notifyEndOfInput();

    while (!destination.isFinished()) {
      destination.attemptRead();
    }

    destination.close();
  }

  private static <V0, V1> V0 convertProtocolObject(final V1 v1, final Class<V0> klass) {
    return Jsons.object(Jsons.jsonNode(v1), klass);
  }

}
