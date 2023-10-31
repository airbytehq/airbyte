/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertAll;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.configoss.WorkerDestinationConfig;
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
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;
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
  protected static final JsonNode SCHEMA;
  static {
    try {
      SCHEMA = Jsons.deserialize(MoreResources.readResource("dat/schema.json"));
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }
  private RecordDiffer DIFFER;

  private String randomSuffix;
  private JsonNode config;
  protected String streamNamespace;
  protected String streamName;
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
   * Utility method for tests to check if table exists
   *
   * @param streamNamespace
   * @param streamName
   * @return
   * @throws Exception
   */
  protected boolean checkTableExists(String streamNamespace, String streamName) {
    // Implementation is specific to destination's tests.
    return true;
  }

  /**
   * For a given stream, return the records that exist in the destination's final table. Each record
   * must be in the format {"_airbyte_raw_id": "...", "_airbyte_extracted_at": "...", "_airbyte_meta":
   * {...}, "field1": ..., "field2": ..., ...}. If the destination renames (e.g. upcases) the airbyte
   * fields, this method must revert that naming to use the exact strings "_airbyte_raw_id", etc.
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

  protected abstract SqlGenerator<?> getSqlGenerator();

  /**
   * Destinations which need to clean up resources after an entire test finishes should override this
   * method. For example, if you want to gracefully close a database connection, you should do that
   * here.
   */
  protected void globalTeardown() throws Exception {}

  /**
   * Conceptually identical to {@link #getFinalMetadataColumnNames()}, but for the raw table.
   */
  protected Map<String, String> getRawMetadataColumnNames() {
    return new HashMap<>();
  }

  /**
   * If the destination connector uses a nonstandard schema for the final table, override this method.
   * For example, destination-snowflake upcases all column names in the final tables.
   * <p>
   * You only need to add mappings for the airbyte metadata column names (_airbyte_raw_id,
   * _airbyte_extracted_at, etc.). The test framework automatically populates mappings for the primary
   * key and cursor using the SqlGenerator.
   */
  protected Map<String, String> getFinalMetadataColumnNames() {
    return new HashMap<>();
  }

  /**
   * @return A suffix which is different for each concurrent test, but stable within a single test.
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

  /**
   * Override this method only when skipping T&D and only compare raw tables and skip final table
   * comparison. For every other case it should always return false.
   *
   * @return
   */
  protected boolean disableFinalTableComparison() {
    return false;
  }

  @BeforeEach
  public void setup() throws Exception {
    config = generateConfig();
    streamNamespace = "typing_deduping_test" + getUniqueSuffix();
    streamName = "test_stream" + getUniqueSuffix();
    streamsToTearDown = new ArrayList<>();

    final SqlGenerator<?> generator = getSqlGenerator();
    DIFFER = new RecordDiffer(
        getRawMetadataColumnNames(),
        getFinalMetadataColumnNames(),
        Pair.of(generator.buildColumnId("id1"), AirbyteProtocolType.INTEGER),
        Pair.of(generator.buildColumnId("id2"), AirbyteProtocolType.INTEGER),
        Pair.of(generator.buildColumnId("updated_at"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE),
        Pair.of(generator.buildColumnId("old_cursor"), AirbyteProtocolType.INTEGER));

    LOGGER.info("Using stream namespace {} and name {}", streamNamespace, streamName);
  }

  @AfterEach
  public void teardown() throws Exception {
    for (final AirbyteStreamNameNamespacePair streamId : streamsToTearDown) {
      teardownStreamAndNamespace(streamId.getNamespace(), streamId.getName());
    }
    globalTeardown();
  }

  /**
   * Starting with an empty destination, execute a full refresh overwrite sync. Verify that the
   * records are written to the destination table. Then run a second sync, and verify that the records
   * are overwritten.
   */
  @Test
  public void fullRefreshOverwrite() throws Exception {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    // First sync
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");

    runSync(catalog, messages1);

    final List<JsonNode> expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison());

    // Second sync
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");

    runSync(catalog, messages2);

    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
  }

  /**
   * Starting with an empty destination, execute a full refresh append sync. Verify that the records
   * are written to the destination table. Then run a second sync, and verify that the old and new
   * records are all present.
   */
  @Test
  public void fullRefreshAppend() throws Exception {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    // First sync
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");

    runSync(catalog, messages1);

    final List<JsonNode> expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison());

    // Second sync
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");

    runSync(catalog, messages2);

    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
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
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
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
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");

    runSync(catalog, messages1);

    final List<JsonNode> expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison());

    // Second sync
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");

    runSync(catalog, messages2);

    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
  }

  /**
   * Starting with an empty destination, execute an incremental dedup sync. Verify that the records
   * are written to the destination table. Then run a second sync, and verify that the raw/final
   * tables contain the correct records.
   */
  @Test
  public void incrementalDedup() throws Exception {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
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
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");

    runSync(catalog, messages1);

    final List<JsonNode> expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison());

    // Second sync
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");

    runSync(catalog, messages2);

    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_incremental_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
  }

  /**
   * Identical to {@link #incrementalDedup()}, except that the stream has no namespace.
   */
  @Test
  public void incrementalDedupDefaultNamespace() throws Exception {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
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
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl", null, streamName);

    runSync(catalog, messages1);

    final List<JsonNode> expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, null, streamName, disableFinalTableComparison());

    // Second sync
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl", null, streamName);

    runSync(catalog, messages2);

    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_incremental_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, null, streamName, disableFinalTableComparison());
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

  /**
   * Run a sync, then remove the {@code name} column from the schema and run a second sync. Verify
   * that the final table doesn't contain the `name` column after the second sync.
   */
  @Test
  public void testIncrementalSyncDropOneColumn() throws Exception {
    final AirbyteStream stream = new AirbyteStream()
        .withNamespace(streamNamespace)
        .withName(streamName)
        .withJsonSchema(SCHEMA);
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(stream)));

    // First sync
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");

    runSync(catalog, messages1);

    final List<JsonNode> expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison());

    // Second sync
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");
    final JsonNode trimmedSchema = SCHEMA.deepCopy();
    ((ObjectNode) trimmedSchema.get("properties")).remove("name");
    stream.setJsonSchema(trimmedSchema);

    runSync(catalog, messages2);

    // The raw data is unaffected by the schema, but the final table should not have a `name` column.
    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl").stream()
        .peek(record -> ((ObjectNode) record).remove(getSqlGenerator().buildColumnId("name").name()))
        .toList();
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
  }

  @Test
  @Disabled("Not yet implemented")
  public void testSyncUsesAirbyteStreamNamespaceIfNotNull() throws Exception {
    // TODO duplicate this test for each sync mode. Run 1st+2nd syncs using a stream with null
    // namespace:
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
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
    final String namespace1 = streamNamespace + "_1";
    final String namespace2 = streamNamespace + "_2";
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
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
    final List<AirbyteMessage> messages1 = Stream.concat(
        readMessages("dat/sync1_messages.jsonl", namespace1, streamName).stream(),
        readMessages("dat/sync1_messages2.jsonl", namespace2, streamName).stream()).toList();

    runSync(catalog, messages1);

    verifySyncResult(
        readRecords("dat/sync1_expectedrecords_raw.jsonl"),
        readRecords("dat/sync1_expectedrecords_dedup_final.jsonl"),
        namespace1,
        streamName, disableFinalTableComparison());
    verifySyncResult(
        readRecords("dat/sync1_expectedrecords_raw2.jsonl"),
        readRecords("dat/sync1_expectedrecords_dedup_final2.jsonl"),
        namespace2,
        streamName, disableFinalTableComparison());

    // Second sync
    final List<AirbyteMessage> messages2 = Stream.concat(
        readMessages("dat/sync2_messages.jsonl", namespace1, streamName).stream(),
        readMessages("dat/sync2_messages2.jsonl", namespace2, streamName).stream()).toList();

    runSync(catalog, messages2);

    verifySyncResult(
        readRecords("dat/sync2_expectedrecords_raw.jsonl"),
        readRecords("dat/sync2_expectedrecords_incremental_dedup_final.jsonl"),
        namespace1,
        streamName, disableFinalTableComparison());
    verifySyncResult(
        readRecords("dat/sync2_expectedrecords_raw2.jsonl"),
        readRecords("dat/sync2_expectedrecords_incremental_dedup_final2.jsonl"),
        namespace2,
        streamName, disableFinalTableComparison());
  }

  /**
   * Run two syncs at the same time. They each have one stream, which has the same name for both syncs
   * but different namespace. This should work fine. This test is similar to
   * {@link #incrementalDedupIdenticalName()}, but uses two separate syncs instead of one sync with
   * two streams.
   * <p>
   * Note that destination stdout is a bit misleading: The two syncs' stdout _should_ be interleaved,
   * but we're just dumping the entire sync1 stdout, and then the entire sync2 stdout.
   */
  @Test
  public void identicalNameSimultaneousSync() throws Exception {
    final String namespace1 = streamNamespace + "_1";
    final ConfiguredAirbyteCatalog catalog1 = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(namespace1)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    final String namespace2 = streamNamespace + "_2";
    final ConfiguredAirbyteCatalog catalog2 = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(namespace2)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl", namespace1, streamName);
    final List<AirbyteMessage> messages2 = readMessages("dat/sync1_messages2.jsonl", namespace2, streamName);

    // Start two concurrent syncs
    final AirbyteDestination sync1 = startSync(catalog1);
    final AirbyteDestination sync2 = startSync(catalog2);
    // Write some messages to both syncs. Write a lot of data to sync 2 to try and force a flush.
    pushMessages(messages1, sync1);
    for (int i = 0; i < 100_000; i++) {
      pushMessages(messages2, sync2);
    }
    // This will dump sync1's entire stdout to our stdout
    endSync(sync1);
    // Write some more messages to the second sync. It should not be affected by the first sync's
    // shutdown.
    for (int i = 0; i < 100_000; i++) {
      pushMessages(messages2, sync2);
    }
    // And this will dump sync2's entire stdout to our stdout
    endSync(sync2);

    // For simplicity, don't verify the raw table. Assume that if the final table is correct, then
    // the raw data is correct. This is generally a safe assumption.
    assertAll(
        () -> DIFFER.diffFinalTableRecords(
            readRecords("dat/sync1_expectedrecords_dedup_final.jsonl"),
            dumpFinalTableRecords(namespace1, streamName)),
        () -> DIFFER.diffFinalTableRecords(
            readRecords("dat/sync1_expectedrecords_dedup_final2.jsonl"),
            dumpFinalTableRecords(namespace2, streamName)));
  }

  @Test
  @Disabled("Not yet implemented")
  public void testSyncNotFailsWithNewFields() throws Exception {
    // TODO duplicate this test for each sync mode. Run a sync, then add a new field to the schema, then
    // run another sync
    // We might want to write a test that verifies more general schema evolution (e.g. all valid
    // evolutions)
  }

  /**
   * Change the cursor column in the second sync to a column that doesn't exist in the first sync.
   * Verify that we overwrite everything correctly.
   * <p>
   * This essentially verifies that the destination connector correctly recognizes NULL cursors as
   * older than non-NULL cursors.
   */
  @Test
  public void incrementalDedupChangeCursor() throws Exception {
    final JsonNode mangledSchema = SCHEMA.deepCopy();
    ((ObjectNode) mangledSchema.get("properties")).remove("updated_at");
    ((ObjectNode) mangledSchema.get("properties")).set(
        "old_cursor",
        Jsons.deserialize(
            """
            {"type": "integer"}
            """));
    final ConfiguredAirbyteStream configuredStream = new ConfiguredAirbyteStream()
        .withSyncMode(SyncMode.INCREMENTAL)
        .withCursorField(List.of("old_cursor"))
        .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
        .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
        .withStream(new AirbyteStream()
            .withNamespace(streamNamespace)
            .withName(streamName)
            .withJsonSchema(mangledSchema));
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(configuredStream));

    // First sync
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_cursorchange_messages.jsonl");

    runSync(catalog, messages1);

    final List<JsonNode> expectedRawRecords1 = readRecords("dat/sync1_cursorchange_expectedrecords_dedup_raw.jsonl");
    final List<JsonNode> expectedFinalRecords1 = readRecords("dat/sync1_cursorchange_expectedrecords_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison());

    // Second sync
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");
    configuredStream.getStream().setJsonSchema(SCHEMA);
    configuredStream.setCursorField(List.of("updated_at"));

    runSync(catalog, messages2);

    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_cursorchange_expectedrecords_incremental_dedup_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_cursorchange_expectedrecords_incremental_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
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

  protected void verifySyncResult(final List<JsonNode> expectedRawRecords,
                                  final List<JsonNode> expectedFinalRecords,
                                  boolean disableFinalTableComparison)
      throws Exception {
    verifySyncResult(expectedRawRecords, expectedFinalRecords, streamNamespace, streamName, disableFinalTableComparison);
  }

  private void verifySyncResult(final List<JsonNode> expectedRawRecords,
                                final List<JsonNode> expectedFinalRecords,
                                final String streamNamespace,
                                final String streamName,
                                boolean disableFinalTableComparison)
      throws Exception {
    final List<JsonNode> actualRawRecords = dumpRawTableRecords(streamNamespace, streamName);
    if (disableFinalTableComparison) {
      DIFFER.diffRawTableRecords(expectedRawRecords, actualRawRecords);
    } else {
      final List<JsonNode> actualFinalRecords = dumpFinalTableRecords(streamNamespace, streamName);
      DIFFER.verifySyncResult(expectedRawRecords, actualRawRecords, expectedFinalRecords, actualFinalRecords);
    }
  }

  public static List<JsonNode> readRecords(final String filename) throws IOException {
    return MoreResources.readResource(filename).lines()
        .map(String::trim)
        .filter(line -> !line.isEmpty())
        .filter(line -> !line.startsWith("//"))
        .map(Jsons::deserializeExact)
        .toList();
  }

  protected List<AirbyteMessage> readMessages(final String filename) throws IOException {
    return readMessages(filename, streamNamespace, streamName);
  }

  private static List<AirbyteMessage> readMessages(final String filename, final String streamNamespace, final String streamName) throws IOException {
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

  protected void runSync(final ConfiguredAirbyteCatalog catalog, final List<AirbyteMessage> messages) throws Exception {
    runSync(catalog, messages, getImageName());
  }

  protected void runSync(final ConfiguredAirbyteCatalog catalog, final List<AirbyteMessage> messages, final String imageName) throws Exception {
    runSync(catalog, messages, imageName, Function.identity());
  }

  protected void runSync(final ConfiguredAirbyteCatalog catalog,
                         final List<AirbyteMessage> messages,
                         final String imageName,
                         Function<JsonNode, JsonNode> configTransformer)
      throws Exception {
    final AirbyteDestination destination = startSync(catalog, imageName, configTransformer);
    pushMessages(messages, destination);
    endSync(destination);
  }

  protected AirbyteDestination startSync(final ConfiguredAirbyteCatalog catalog) throws Exception {
    return startSync(catalog, getImageName());
  }

  protected AirbyteDestination startSync(final ConfiguredAirbyteCatalog catalog, final String imageName) throws Exception {
    return startSync(catalog, imageName, Function.identity());
  }

  /**
   *
   * @param catalog
   * @param imageName
   * @param configTransformer - test specific config overrides or additions can be performed with this
   *        function
   * @return
   * @throws Exception
   */
  protected AirbyteDestination startSync(final ConfiguredAirbyteCatalog catalog,
                                         final String imageName,
                                         Function<JsonNode, JsonNode> configTransformer)
      throws Exception {
    synchronized (this) {
      catalog.getStreams().forEach(s -> streamsToTearDown.add(AirbyteStreamNameNamespacePair.fromAirbyteStream(s.getStream())));
    }

    final Path testDir = Path.of("/tmp/airbyte_tests/");
    Files.createDirectories(testDir);
    final Path workspaceRoot = Files.createTempDirectory(testDir, "test");
    final Path jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"));
    final Path localRoot = Files.createTempDirectory(testDir, "output");
    final ProcessFactory processFactory = new DockerProcessFactory(
        workspaceRoot,
        workspaceRoot.toString(),
        localRoot.toString(),
        "host",
        Collections.emptyMap());
    final JsonNode transformedConfig = configTransformer.apply(config);
    final WorkerDestinationConfig destinationConfig = new WorkerDestinationConfig()
        .withConnectionId(UUID.randomUUID())
        .withCatalog(convertProtocolObject(catalog, io.airbyte.protocol.models.ConfiguredAirbyteCatalog.class))
        .withDestinationConnectionConfiguration(transformedConfig);

    final AirbyteDestination destination = new DefaultAirbyteDestination(new AirbyteIntegrationLauncher(
        "0",
        0,
        imageName,
        processFactory,
        null,
        null,
        false,
        new EnvVariableFeatureFlags()));

    destination.start(destinationConfig, jobRoot, Collections.emptyMap());

    return destination;
  }

  private static void pushMessages(final List<AirbyteMessage> messages, final AirbyteDestination destination) {
    messages.forEach(
        message -> Exceptions.toRuntime(() -> destination.accept(convertProtocolObject(message, io.airbyte.protocol.models.AirbyteMessage.class))));
  }

  // TODO Eventually we'll want to somehow extract the state messages while a sync is running, to
  // verify checkpointing.
  // That's going to require some nontrivial changes to how attemptRead() works.
  private static void endSync(final AirbyteDestination destination) throws Exception {
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
