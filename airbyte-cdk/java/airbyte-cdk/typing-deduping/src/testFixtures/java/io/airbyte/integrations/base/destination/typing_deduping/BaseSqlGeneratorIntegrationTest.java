/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Streams;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Instant;
import java.util.Arrays;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class exercises {@link SqlGenerator} implementations. All destinations should extend this
 * class for their respective implementation. Subclasses are encouraged to add additional tests with
 * destination-specific behavior (for example, verifying that datasets are created in the correct
 * BigQuery region).
 * <p>
 * Subclasses should implement a {@link org.junit.jupiter.api.BeforeAll} method to load any secrets
 * and connect to the destination. This test expects to be able to run
 * {@link #getDestinationHandler()} in a {@link org.junit.jupiter.api.BeforeEach} method.
 */
@Execution(ExecutionMode.CONCURRENT)
public abstract class BaseSqlGeneratorIntegrationTest<DialectTableDefinition> {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseSqlGeneratorIntegrationTest.class);
  /**
   * This, along with {@link #FINAL_TABLE_COLUMN_NAMES_CDC}, is the list of columns that should be in
   * the final table. They're useful for generating SQL queries to insert records into the final
   * table.
   */
  protected static final List<String> FINAL_TABLE_COLUMN_NAMES = List.of(
      "_airbyte_raw_id",
      "_airbyte_extracted_at",
      "_airbyte_meta",
      "id1",
      "id2",
      "updated_at",
      "struct",
      "array",
      "string",
      "number",
      "integer",
      "boolean",
      "timestamp_with_timezone",
      "timestamp_without_timezone",
      "time_with_timezone",
      "time_without_timezone",
      "date",
      "unknown");
  protected static final List<String> FINAL_TABLE_COLUMN_NAMES_CDC;

  static {
    FINAL_TABLE_COLUMN_NAMES_CDC = Streams.concat(
        FINAL_TABLE_COLUMN_NAMES.stream(),
        Stream.of("_ab_cdc_deleted_at")).toList();
  }

  protected RecordDiffer DIFFER;

  /**
   * Subclasses may use these four StreamConfigs in their tests.
   */
  protected StreamConfig incrementalDedupStream;
  /**
   * We intentionally don't have full refresh overwrite/append streams. Those actually behave
   * identically in the sqlgenerator. Overwrite mode is actually handled in
   * {@link DefaultTyperDeduper}.
   */
  protected StreamConfig incrementalAppendStream;
  protected StreamConfig cdcIncrementalDedupStream;
  /**
   * This isn't particularly realistic, but it's technically possible.
   */
  protected StreamConfig cdcIncrementalAppendStream;

  protected SqlGenerator<DialectTableDefinition> generator;
  protected DestinationHandler<DialectTableDefinition> destinationHandler;
  protected String namespace;

  protected StreamId streamId;
  private List<ColumnId> primaryKey;
  private ColumnId cursor;
  private LinkedHashMap<ColumnId, AirbyteType> COLUMNS;

  protected abstract SqlGenerator<DialectTableDefinition> getSqlGenerator();

  protected abstract DestinationHandler<DialectTableDefinition> getDestinationHandler();

  /**
   * Subclasses should override this method if they need to make changes to the stream ID. For
   * example, you could upcase the final table name here.
   */
  protected StreamId buildStreamId(final String namespace, final String finalTableName, final String rawTableName) {
    return new StreamId(namespace, finalTableName, namespace, rawTableName, namespace, finalTableName);
  }

  /**
   * Do any setup work to create a namespace for this test run. For example, this might create a
   * BigQuery dataset, or a Snowflake schema.
   */
  protected abstract void createNamespace(String namespace) throws Exception;

  /**
   * Create a raw table using the StreamId's rawTableId.
   */
  protected abstract void createRawTable(StreamId streamId) throws Exception;

  /**
   * Creates a raw table in the v1 format
   */
  protected abstract void createV1RawTable(StreamId v1RawTable) throws Exception;

  protected abstract void insertRawTableRecords(StreamId streamId, List<JsonNode> records) throws Exception;

  protected abstract void insertV1RawTableRecords(StreamId streamId, List<JsonNode> records) throws Exception;

  protected abstract void insertFinalTableRecords(boolean includeCdcDeletedAt, StreamId streamId, String suffix, List<JsonNode> records)
      throws Exception;

  /**
   * The two dump methods are defined identically as in {@link BaseTypingDedupingTest}, but with
   * slightly different method signature. This test expects subclasses to respect the raw/finalTableId
   * on the StreamId object, rather than hardcoding e.g. the airbyte_internal dataset.
   * <p>
   * The {@code _airbyte_data} field must be deserialized into an ObjectNode, even if it's stored in
   * the destination as a string.
   */
  protected abstract List<JsonNode> dumpRawTableRecords(StreamId streamId) throws Exception;

  protected abstract List<JsonNode> dumpFinalTableRecords(StreamId streamId, String suffix) throws Exception;

  /**
   * Clean up all resources in the namespace. For example, this might delete the BigQuery dataset
   * created in {@link #createNamespace(String)}.
   */
  protected abstract void teardownNamespace(String namespace) throws Exception;

  /**
   * Identical to {@link BaseTypingDedupingTest#getRawMetadataColumnNames()}.
   */
  protected Map<String, String> getRawMetadataColumnNames() {
    return new HashMap<>();
  }

  /**
   * Identical to {@link BaseTypingDedupingTest#getFinalMetadataColumnNames()}.
   */
  protected Map<String, String> getFinalMetadataColumnNames() {
    return new HashMap<>();
  }

  /**
   * This test implementation is extremely destination-specific, but all destinations must implement
   * it. This test should verify that creating a table using {@link #incrementalDedupStream} works as
   * expected, including column types, indexing, partitioning, etc.
   * <p>
   * Note that subclasses must also annotate their implementation with @Test.
   */
  @Test
  public abstract void testCreateTableIncremental() throws Exception;

  @BeforeEach
  public void setup() throws Exception {
    generator = getSqlGenerator();
    destinationHandler = getDestinationHandler();
    final ColumnId id1 = generator.buildColumnId("id1");
    final ColumnId id2 = generator.buildColumnId("id2");
    primaryKey = List.of(id1, id2);
    cursor = generator.buildColumnId("updated_at");

    COLUMNS = new LinkedHashMap<>();
    COLUMNS.put(id1, AirbyteProtocolType.INTEGER);
    COLUMNS.put(id2, AirbyteProtocolType.INTEGER);
    COLUMNS.put(cursor, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    COLUMNS.put(generator.buildColumnId("struct"), new Struct(new LinkedHashMap<>()));
    COLUMNS.put(generator.buildColumnId("array"), new Array(AirbyteProtocolType.UNKNOWN));
    COLUMNS.put(generator.buildColumnId("string"), AirbyteProtocolType.STRING);
    COLUMNS.put(generator.buildColumnId("number"), AirbyteProtocolType.NUMBER);
    COLUMNS.put(generator.buildColumnId("integer"), AirbyteProtocolType.INTEGER);
    COLUMNS.put(generator.buildColumnId("boolean"), AirbyteProtocolType.BOOLEAN);
    COLUMNS.put(generator.buildColumnId("timestamp_with_timezone"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    COLUMNS.put(generator.buildColumnId("timestamp_without_timezone"), AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE);
    COLUMNS.put(generator.buildColumnId("time_with_timezone"), AirbyteProtocolType.TIME_WITH_TIMEZONE);
    COLUMNS.put(generator.buildColumnId("time_without_timezone"), AirbyteProtocolType.TIME_WITHOUT_TIMEZONE);
    COLUMNS.put(generator.buildColumnId("date"), AirbyteProtocolType.DATE);
    COLUMNS.put(generator.buildColumnId("unknown"), AirbyteProtocolType.UNKNOWN);

    final LinkedHashMap<ColumnId, AirbyteType> cdcColumns = new LinkedHashMap<>(COLUMNS);
    cdcColumns.put(generator.buildColumnId("_ab_cdc_deleted_at"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);

    DIFFER = new RecordDiffer(
        getRawMetadataColumnNames(),
        getFinalMetadataColumnNames(),
        Pair.of(id1, AirbyteProtocolType.INTEGER),
        Pair.of(id2, AirbyteProtocolType.INTEGER),
        Pair.of(cursor, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE));

    namespace = Strings.addRandomSuffix("sql_generator_test", "_", 5);
    // This is not a typical stream ID would look like, but SqlGenerator isn't allowed to make any
    // assumptions about StreamId structure.
    // In practice, the final table would be testDataset.users, and the raw table would be
    // airbyte_internal.testDataset_raw__stream_users.
    streamId = buildStreamId(namespace, "users_final", "users_raw");

    incrementalDedupStream = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        primaryKey,
        Optional.of(cursor),
        COLUMNS);
    incrementalAppendStream = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND,
        primaryKey,
        Optional.of(cursor),
        COLUMNS);

    cdcIncrementalDedupStream = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        primaryKey,
        Optional.of(cursor),
        cdcColumns);
    cdcIncrementalAppendStream = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND,
        primaryKey,
        Optional.of(cursor),
        cdcColumns);

    LOGGER.info("Running with namespace {}", namespace);
    createNamespace(namespace);
  }

  @AfterEach
  public void teardown() throws Exception {
    teardownNamespace(namespace);
  }

  /**
   * Create a table and verify that we correctly recognize it as identical to itself.
   */
  @Test
  public void detectNoSchemaChange() throws Exception {
    final String createTable = generator.createTable(incrementalDedupStream, "", false);
    destinationHandler.execute(createTable);

    final Optional<DialectTableDefinition> existingTable = destinationHandler.findExistingTable(streamId);
    if (!existingTable.isPresent()) {
      fail("Destination handler could not find existing table");
    }

    assertTrue(
        generator.existingSchemaMatchesStreamConfig(incrementalDedupStream, existingTable.get()),
        "Unchanged schema was incorrectly detected as a schema change.");
  }

  /**
   * Verify that adding a new column is detected as a schema change.
   */
  @Test
  public void detectColumnAdded() throws Exception {
    final String createTable = generator.createTable(incrementalDedupStream, "", false);
    destinationHandler.execute(createTable);

    final Optional<DialectTableDefinition> existingTable = destinationHandler.findExistingTable(streamId);
    if (!existingTable.isPresent()) {
      fail("Destination handler could not find existing table");
    }

    incrementalDedupStream.columns().put(
        generator.buildColumnId("new_column"),
        AirbyteProtocolType.STRING);

    assertFalse(
        generator.existingSchemaMatchesStreamConfig(incrementalDedupStream, existingTable.get()),
        "Adding a new column was not detected as a schema change.");
  }

  /**
   * Verify that removing a column is detected as a schema change.
   */
  @Test
  public void detectColumnRemoved() throws Exception {
    final String createTable = generator.createTable(incrementalDedupStream, "", false);
    destinationHandler.execute(createTable);

    final Optional<DialectTableDefinition> existingTable = destinationHandler.findExistingTable(streamId);
    if (!existingTable.isPresent()) {
      fail("Destination handler could not find existing table");
    }

    incrementalDedupStream.columns().remove(generator.buildColumnId("string"));

    assertFalse(
        generator.existingSchemaMatchesStreamConfig(incrementalDedupStream, existingTable.get()),
        "Removing a column was not detected as a schema change.");
  }

  /**
   * Verify that changing a column's type is detected as a schema change.
   */
  @Test
  public void detectColumnChanged() throws Exception {
    final String createTable = generator.createTable(incrementalDedupStream, "", false);
    destinationHandler.execute(createTable);

    final Optional<DialectTableDefinition> existingTable = destinationHandler.findExistingTable(streamId);
    if (!existingTable.isPresent()) {
      fail("Destination handler could not find existing table");
    }

    incrementalDedupStream.columns().put(
        generator.buildColumnId("string"),
        AirbyteProtocolType.INTEGER);

    assertFalse(
        generator.existingSchemaMatchesStreamConfig(incrementalDedupStream, existingTable.get()),
        "Altering a column was not detected as a schema change.");
  }

  /**
   * Test that T+D supports streams whose name and namespace are the same.
   */
  @Test
  public void incrementalDedupSameNameNamespace() throws Exception {
    final StreamId streamId = buildStreamId(namespace, namespace, namespace + "_raw");
    final StreamConfig stream = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        incrementalDedupStream.primaryKey(),
        incrementalDedupStream.cursor(),
        incrementalDedupStream.columns());

    createRawTable(streamId);
    createFinalTable(stream, "");
    insertRawTableRecords(
        streamId,
        List.of(Jsons.deserialize(
            """
            {
              "_airbyte_raw_id": "5ce60e70-98aa-4fe3-8159-67207352c4f0",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_data": {"id1": 1, "id2": 100}
            }
            """)));

    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, stream, Optional.empty(), "");

    final List<JsonNode> rawRecords = dumpRawTableRecords(streamId);
    final List<JsonNode> finalRecords = dumpFinalTableRecords(streamId, "");
    verifyRecordCounts(1, rawRecords, 1, finalRecords);
  }

  /**
   * Run a full T+D update for an incremental-dedup stream, writing to a final table with "_foo"
   * suffix, with values for all data types. Verifies all behaviors for all types:
   * <ul>
   * <li>A valid, nonnull value</li>
   * <li>No value (i.e. the column is missing from the record)</li>
   * <li>A JSON null value</li>
   * <li>An invalid value</li>
   * </ul>
   * <p>
   * In practice, incremental streams never write to a suffixed table, but SqlGenerator isn't allowed
   * to make that assumption (and we might as well exercise that code path).
   */
  @Test
  public void allTypes() throws Exception {
    createRawTable(streamId);
    createFinalTable(incrementalDedupStream, "_foo");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/alltypes_inputrecords.jsonl"));

    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, incrementalDedupStream, Optional.empty(), "_foo");

    verifyRecords(
        "sqlgenerator/alltypes_expectedrecords_raw.jsonl",
        dumpRawTableRecords(streamId),
        "sqlgenerator/alltypes_expectedrecords_final.jsonl",
        dumpFinalTableRecords(streamId, "_foo"));
  }

  /**
   * Run through some plausible T+D scenarios to verify that we correctly identify the min raw
   * timestamp.
   */
  @Test
  public void minTimestampBehavesCorrectly() throws Exception {
    // When the raw table doesn't exist, there is no timestamp
    assertEquals(Optional.empty(), destinationHandler.getMinTimestampForSync(streamId));

    // When the raw table is empty, there is no timestamp
    createRawTable(streamId);
    assertEquals(Optional.empty(), destinationHandler.getMinTimestampForSync(streamId));

    // If we insert some raw records with null loaded_at, we should get the min extracted_at
    insertRawTableRecords(
        streamId,
        List.of(
            Jsons.deserialize(
                """
                {
                  "_airbyte_raw_id": "899d3bc3-7921-44f0-8517-c748a28fe338",
                  "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                  "_airbyte_data": {}
                }
                """),
            Jsons.deserialize(
                """
                {
                  "_airbyte_raw_id": "47f46eb6-fcae-469c-a7fc-31d4b9ce7474",
                  "_airbyte_extracted_at": "2023-01-02T00:00:00Z",
                  "_airbyte_data": {}
                }
                """)));
    Instant actualTimestamp = destinationHandler.getMinTimestampForSync(streamId).get();
    assertTrue(
        actualTimestamp.isBefore(Instant.parse("2023-01-01T00:00:00Z")),
        "When all raw records have null loaded_at, the min timestamp should be earlier than all of their extracted_at values (2023-01-01). Was actually "
            + actualTimestamp);

    // Execute T+D to set loaded_at on the records
    createFinalTable(incrementalAppendStream, "");
    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, incrementalAppendStream, Optional.empty(), "");

    assertEquals(
        destinationHandler.getMinTimestampForSync(streamId).get(),
        Instant.parse("2023-01-02T00:00:00Z"),
        "When all raw records have non-null loaded_at, the min timestamp should be equal to the latest extracted_at");

    // If we insert another raw record with older extracted_at than the typed records, we should fetch a
    // timestamp earlier than this new record.
    // This emulates a sync inserting some records out of order, running T+D on newer records, inserting
    // an older record, and then crashing before it can execute T+D. The next sync should recognize
    // that older record as still needing to be processed.
    insertRawTableRecords(
        streamId,
        List.of(Jsons.deserialize(
            """
            {
              "_airbyte_raw_id": "899d3bc3-7921-44f0-8517-c748a28fe338",
              "_airbyte_extracted_at": "2023-01-01T12:00:00Z",
              "_airbyte_data": {}
            }
            """)));
    actualTimestamp = destinationHandler.getMinTimestampForSync(streamId).get();
    // this is a pretty confusing pair of assertions. To explain them in more detail: There are three
    // records in the raw table:
    // * loaded_at not null, extracted_at = 2023-01-01 00:00Z
    // * loaded_at is null, extracted_at = 2023-01-01 12:00Z
    // * loaded_at not null, extracted_at = 2023-01-02 00:00Z
    // We should have a timestamp which is older than the second record, but newer than or equal to
    // (i.e. not before) the first record. This allows us to query the raw table using
    // `_airbyte_extracted_at > ?`, which will include the second record and exclude the first record.
    assertTrue(
        actualTimestamp.isBefore(Instant.parse("2023-01-01T12:00:00Z")),
        "When some raw records have null loaded_at, the min timestamp should be earlier than the oldest unloaded record (2023-01-01 12:00Z). Was actually "
            + actualTimestamp);
    assertFalse(
        actualTimestamp.isBefore(Instant.parse("2023-01-01T00:00:00Z")),
        "When some raw records have null loaded_at, the min timestamp should be later than the newest loaded record older than the oldest unloaded record (2023-01-01 00:00Z). Was actually "
            + actualTimestamp);
  }

  /**
   * Identical to {@link #allTypes()}, but queries for the min raw timestamp first. This verifies that
   * if a previous sync doesn't fully type-and-dedupe a table, we still get those records on the next
   * sync.
   */
  @Test
  public void handlePreexistingRecords() throws Exception {
    createRawTable(streamId);
    createFinalTable(incrementalDedupStream, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/alltypes_inputrecords.jsonl"));

    final Optional<Instant> minTimestampForSync = destinationHandler.getMinTimestampForSync(streamId);
    assertTrue(minTimestampForSync.isPresent(), "After writing some raw records, the min timestamp should be present.");

    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, incrementalDedupStream, minTimestampForSync, "");

    verifyRecords(
        "sqlgenerator/alltypes_expectedrecords_raw.jsonl",
        dumpRawTableRecords(streamId),
        "sqlgenerator/alltypes_expectedrecords_final.jsonl",
        dumpFinalTableRecords(streamId, ""));
  }

  /**
   * Identical to {@link #handlePreexistingRecords()}, but queries for the min timestamp before
   * inserting any raw records. This emulates a sync starting with an empty table.
   */
  @Test
  public void handleNoPreexistingRecords() throws Exception {
    createRawTable(streamId);
    final Optional<Instant> minTimestampForSync = destinationHandler.getMinTimestampForSync(streamId);
    assertEquals(Optional.empty(), minTimestampForSync);

    createFinalTable(incrementalDedupStream, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/alltypes_inputrecords.jsonl"));

    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, incrementalDedupStream, minTimestampForSync, "");

    verifyRecords(
        "sqlgenerator/alltypes_expectedrecords_raw.jsonl",
        dumpRawTableRecords(streamId),
        "sqlgenerator/alltypes_expectedrecords_final.jsonl",
        dumpFinalTableRecords(streamId, ""));
  }

  /**
   * Verify that we correctly only process raw records with recent extracted_at. In practice,
   * destinations should not do this - but their SQL should work correctly.
   * <p>
   * Create two raw records, one with an old extracted_at. Verify that updatedTable only T+Ds the new
   * record, and doesn't set loaded_at on the old record.
   */
  @Test
  public void ignoreOldRawRecords() throws Exception {
    createRawTable(streamId);
    createFinalTable(incrementalAppendStream, "");
    insertRawTableRecords(
        streamId,
        List.of(
            Jsons.deserialize(
                """
                {
                  "_airbyte_raw_id": "c5bcae50-962e-4b92-b2eb-1659eae31693",
                  "_airbyte_extracted_at": "2022-01-01T00:00:00Z",
                  "_airbyte_data": {
                    "string": "foo"
                  }
                }
                """),
            Jsons.deserialize(
                """
                {
                  "_airbyte_raw_id": "93f1bdd8-1916-4e6c-94dc-29a5d9701179",
                  "_airbyte_extracted_at": "2023-01-01T01:00:00Z",
                  "_airbyte_data": {
                    "string": "bar"
                  }
                }
                """)));

    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, incrementalAppendStream,
        Optional.of(Instant.parse("2023-01-01T00:00:00Z")), "");

    final List<JsonNode> rawRecords = dumpRawTableRecords(streamId);
    final List<JsonNode> finalRecords = dumpFinalTableRecords(streamId, "");
    assertAll(
        () -> assertEquals(
            1,
            rawRecords.stream().filter(record -> record.get("_airbyte_loaded_at") == null).count(),
            "Raw table should only have non-null loaded_at on the newer record"),
        () -> assertEquals(1, finalRecords.size(), "T+D should only execute on the newer record"));
  }

  /**
   * Test JSON Types encounted for a String Type field.
   *
   * @throws Exception
   */
  @Test
  public void jsonStringifyTypes() throws Exception {
    createRawTable(streamId);
    createFinalTable(incrementalDedupStream, "_foo");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/json_types_in_string_inputrecords.jsonl"));
    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, incrementalDedupStream, Optional.empty(), "_foo");
    verifyRecords(
        "sqlgenerator/json_types_in_string_expectedrecords_raw.jsonl",
        dumpRawTableRecords(streamId),
        "sqlgenerator/json_types_in_string_expectedrecords_final.jsonl",
        dumpFinalTableRecords(streamId, "_foo"));
  }

  @Test
  public void timestampFormats() throws Exception {
    createRawTable(streamId);
    createFinalTable(incrementalAppendStream, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/timestampformats_inputrecords.jsonl"));

    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, incrementalAppendStream, Optional.empty(), "");

    DIFFER.diffFinalTableRecords(
        BaseTypingDedupingTest.readRecords("sqlgenerator/timestampformats_expectedrecords_final.jsonl"),
        dumpFinalTableRecords(streamId, ""));
  }

  @Test
  public void incrementalDedup() throws Exception {
    createRawTable(streamId);
    createFinalTable(incrementalDedupStream, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/incrementaldedup_inputrecords.jsonl"));

    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, incrementalDedupStream, Optional.empty(), "");

    verifyRecords(
        "sqlgenerator/incrementaldedup_expectedrecords_raw.jsonl",
        dumpRawTableRecords(streamId),
        "sqlgenerator/incrementaldedup_expectedrecords_final.jsonl",
        dumpFinalTableRecords(streamId, ""));
  }

  /**
   * We shouldn't crash on a sync with null cursor. Insert two records and verify that we keep the
   * record with higher extracted_at.
   */
  @Test
  public void incrementalDedupNoCursor() throws Exception {
    final StreamConfig streamConfig = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        primaryKey,
        Optional.empty(),
        COLUMNS);
    createRawTable(streamId);
    createFinalTable(streamConfig, "");
    insertRawTableRecords(
        streamId,
        List.of(
            Jsons.deserialize(
                """
                {
                  "_airbyte_raw_id": "c5bcae50-962e-4b92-b2eb-1659eae31693",
                  "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                  "_airbyte_data": {
                    "id1": 1,
                    "id2": 100,
                    "string": "foo"
                  }
                }
                """),
            Jsons.deserialize(
                """
                {
                  "_airbyte_raw_id": "93f1bdd8-1916-4e6c-94dc-29a5d9701179",
                  "_airbyte_extracted_at": "2023-01-01T01:00:00Z",
                  "_airbyte_data": {
                    "id1": 1,
                    "id2": 100,
                    "string": "bar"
                  }
                }
                """)));

    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, streamConfig, Optional.empty(), "");

    final List<JsonNode> actualRawRecords = dumpRawTableRecords(streamId);
    final List<JsonNode> actualFinalRecords = dumpFinalTableRecords(streamId, "");
    verifyRecordCounts(
        2,
        actualRawRecords,
        1,
        actualFinalRecords);
    assertEquals("bar", actualFinalRecords.get(0).get(generator.buildColumnId("string").name()).asText());
  }

  @Test
  public void incrementalAppend() throws Exception {
    createRawTable(streamId);
    createFinalTable(incrementalAppendStream, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/incrementaldedup_inputrecords.jsonl"));

    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, incrementalAppendStream, Optional.empty(), "");

    verifyRecordCounts(
        3,
        dumpRawTableRecords(streamId),
        3,
        dumpFinalTableRecords(streamId, ""));
  }

  /**
   * Create a nonempty users_final_tmp table. Overwrite users_final from users_final_tmp. Verify that
   * users_final now exists and contains nonzero records.
   */
  @Test
  public void overwriteFinalTable() throws Exception {
    createFinalTable(incrementalAppendStream, "_tmp");
    final List<JsonNode> records = singletonList(Jsons.deserialize(
        """
        {
          "_airbyte_raw_id": "4fa4efe2-3097-4464-bd22-11211cc3e15b",
          "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
          "_airbyte_meta": {}
        }
        """));
    insertFinalTableRecords(
        false,
        streamId,
        "_tmp",
        records);

    final String sql = generator.overwriteFinalTable(streamId, "_tmp");
    destinationHandler.execute(sql);

    assertEquals(1, dumpFinalTableRecords(streamId, "").size());
  }

  @Test
  public void cdcImmediateDeletion() throws Exception {
    createRawTable(streamId);
    createFinalTable(cdcIncrementalDedupStream, "");
    insertRawTableRecords(
        streamId,
        singletonList(Jsons.deserialize(
            """
            {
              "_airbyte_raw_id": "4fa4efe2-3097-4464-bd22-11211cc3e15b",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_data": {
                "id1": 1,
                "id2": 100,
                "updated_at": "2023-01-01T00:00:00Z",
                "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"
              }
            }
            """)));

    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, cdcIncrementalDedupStream, Optional.empty(), "");

    verifyRecordCounts(
        1,
        dumpRawTableRecords(streamId),
        0,
        dumpFinalTableRecords(streamId, ""));
  }

  /**
   * Verify that running T+D twice is idempotent. Previously there was a bug where non-dedup syncs
   * with an _ab_cdc_deleted_at column would duplicate "deleted" records on each run.
   */
  @Test
  public void cdcIdempotent() throws Exception {
    createRawTable(streamId);
    createFinalTable(cdcIncrementalAppendStream, "");
    insertRawTableRecords(
        streamId,
        singletonList(Jsons.deserialize(
            """
            {
              "_airbyte_raw_id": "4fa4efe2-3097-4464-bd22-11211cc3e15b",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_data": {
                "id1": 1,
                "id2": 100,
                "updated_at": "2023-01-01T00:00:00Z",
                "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"
              }
            }
            """)));

    // Execute T+D twice
    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, cdcIncrementalAppendStream, Optional.empty(), "");
    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, cdcIncrementalAppendStream, Optional.empty(), "");

    verifyRecordCounts(
        1,
        dumpRawTableRecords(streamId),
        1,
        dumpFinalTableRecords(streamId, ""));
  }

  @Test
  public void cdcComplexUpdate() throws Exception {
    createRawTable(streamId);
    createFinalTable(cdcIncrementalDedupStream, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/cdcupdate_inputrecords_raw.jsonl"));
    insertFinalTableRecords(
        true,
        streamId,
        "",
        BaseTypingDedupingTest.readRecords("sqlgenerator/cdcupdate_inputrecords_final.jsonl"));

    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, cdcIncrementalDedupStream, Optional.empty(), "");

    verifyRecordCounts(
        11,
        dumpRawTableRecords(streamId),
        6,
        dumpFinalTableRecords(streamId, ""));
  }

  /**
   * source operations:
   * <ol>
   * <li>insert id=1 (lsn 10000)</li>
   * <li>delete id=1 (lsn 10001)</li>
   * </ol>
   * <p>
   * But the destination writes lsn 10001 before 10000. We should still end up with no records in the
   * final table.
   * <p>
   * All records have the same emitted_at timestamp. This means that we live or die purely based on
   * our ability to use _ab_cdc_lsn.
   */
  @Test
  public void testCdcOrdering_updateAfterDelete() throws Exception {
    createRawTable(streamId);
    createFinalTable(cdcIncrementalDedupStream, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/cdcordering_updateafterdelete_inputrecords.jsonl"));

    final Optional<Instant> minTimestampForSync = destinationHandler.getMinTimestampForSync(cdcIncrementalDedupStream.id());
    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, cdcIncrementalDedupStream, minTimestampForSync, "");

    verifyRecordCounts(
        2,
        dumpRawTableRecords(streamId),
        0,
        dumpFinalTableRecords(streamId, ""));
  }

  /**
   * source operations:
   * <ol>
   * <li>arbitrary history...</li>
   * <li>delete id=1 (lsn 10001)</li>
   * <li>reinsert id=1 (lsn 10002)</li>
   * </ol>
   * <p>
   * But the destination receives LSNs 10002 before 10001. In this case, we should keep the reinserted
   * record in the final table.
   * <p>
   * All records have the same emitted_at timestamp. This means that we live or die purely based on
   * our ability to use _ab_cdc_lsn.
   */
  @Test
  public void testCdcOrdering_insertAfterDelete() throws Exception {
    createRawTable(streamId);
    createFinalTable(cdcIncrementalDedupStream, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/cdcordering_insertafterdelete_inputrecords_raw.jsonl"));
    insertFinalTableRecords(
        true,
        streamId,
        "",
        BaseTypingDedupingTest.readRecords("sqlgenerator/cdcordering_insertafterdelete_inputrecords_final.jsonl"));

    final Optional<Instant> minTimestampForSync = destinationHandler.getMinTimestampForSync(cdcIncrementalAppendStream.id());
    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, cdcIncrementalDedupStream, minTimestampForSync, "");
    verifyRecordCounts(
        2,
        dumpRawTableRecords(streamId),
        1,
        dumpFinalTableRecords(streamId, ""));
  }

  /**
   * Create a table which includes the _ab_cdc_deleted_at column, then soft reset it using the non-cdc
   * stream config. Verify that the deleted_at column gets dropped.
   */
  @Test
  public void softReset() throws Exception {
    createRawTable(streamId);
    createFinalTable(cdcIncrementalAppendStream, "");
    insertRawTableRecords(
        streamId,
        singletonList(Jsons.deserialize(
            """
            {
              "_airbyte_raw_id": "arst",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_loaded_at": "2023-01-01T00:00:00Z",
              "_airbyte_data": {
                "id1": 1,
                "id2": 100,
                "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"
              }
            }
            """)));
    insertFinalTableRecords(
        true,
        streamId,
        "",
        singletonList(Jsons.deserialize(
            """
            {
              "_airbyte_raw_id": "arst",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_meta": {},
              "id1": 1,
              "id2": 100,
              "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"
            }
            """)));

    TypeAndDedupeTransaction.executeSoftReset(generator, destinationHandler, incrementalAppendStream);

    final List<JsonNode> actualRawRecords = dumpRawTableRecords(streamId);
    final List<JsonNode> actualFinalRecords = dumpFinalTableRecords(streamId, "");
    assertAll(
        () -> assertEquals(1, actualRawRecords.size()),
        () -> assertEquals(1, actualFinalRecords.size()),
        () -> assertTrue(
            actualFinalRecords.stream().noneMatch(record -> record.has("_ab_cdc_deleted_at")),
            "_ab_cdc_deleted_at column was expected to be dropped. Actual final table had: " + actualFinalRecords));
  }

  @Test
  public void weirdColumnNames() throws Exception {
    createRawTable(streamId);
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/weirdcolumnnames_inputrecords_raw.jsonl"));
    final StreamConfig stream = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        primaryKey,
        Optional.of(cursor),
        new LinkedHashMap<>() {

          {
            put(generator.buildColumnId("id1"), AirbyteProtocolType.INTEGER);
            put(generator.buildColumnId("id2"), AirbyteProtocolType.INTEGER);
            put(generator.buildColumnId("updated_at"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
            put(generator.buildColumnId("$starts_with_dollar_sign"), AirbyteProtocolType.STRING);
            put(generator.buildColumnId("includes\"doublequote"), AirbyteProtocolType.STRING);
            put(generator.buildColumnId("includes'singlequote"), AirbyteProtocolType.STRING);
            put(generator.buildColumnId("includes`backtick"), AirbyteProtocolType.STRING);
            put(generator.buildColumnId("includes.period"), AirbyteProtocolType.STRING);
            put(generator.buildColumnId("includes$$doubledollar"), AirbyteProtocolType.STRING);
            put(generator.buildColumnId("endswithbackslash\\"), AirbyteProtocolType.STRING);
          }

        });

    final String createTable = generator.createTable(stream, "", false);
    destinationHandler.execute(createTable);
    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, stream, Optional.empty(), "");

    verifyRecords(
        "sqlgenerator/weirdcolumnnames_expectedrecords_raw.jsonl",
        dumpRawTableRecords(streamId),
        "sqlgenerator/weirdcolumnnames_expectedrecords_final.jsonl",
        dumpFinalTableRecords(streamId, ""));
  }

  /**
   * Verify that we don't crash when there are special characters in the stream namespace, name,
   * primary key, or cursor.
   */
  @ParameterizedTest
  @ValueSource(strings = {"$", "${", "${${", "${foo}", "\"", "'", "`", ".", "$$", "\\", "{", "}"})
  public void noCrashOnSpecialCharacters(final String specialChars) throws Exception {
    final String str = specialChars + "_" + namespace + "_" + specialChars;
    final StreamId originalStreamId = generator.buildStreamId(str, str, "unused");
    final StreamId modifiedStreamId = buildStreamId(
        originalStreamId.finalNamespace(),
        originalStreamId.finalName(),
        "raw_table");
    final ColumnId columnId = generator.buildColumnId(str);
    try {
      createNamespace(modifiedStreamId.finalNamespace());
      createRawTable(modifiedStreamId);
      insertRawTableRecords(
          modifiedStreamId,
          List.of(Jsons.jsonNode(Map.of(
              "_airbyte_raw_id", "758989f2-b148-4dd3-8754-30d9c17d05fb",
              "_airbyte_extracted_at", "2023-01-01T00:00:00Z",
              "_airbyte_data", Map.of(str, "bar")))));
      final StreamConfig stream = new StreamConfig(
          modifiedStreamId,
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP,
          List.of(columnId),
          Optional.of(columnId),
          new LinkedHashMap<>() {

            {
              put(columnId, AirbyteProtocolType.STRING);
            }

          });

      final String createTable = generator.createTable(stream, "", false);
      destinationHandler.execute(createTable);
      // Not verifying anything about the data; let's just make sure we don't crash.
      TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, stream, Optional.empty(), "");
    } finally {
      teardownNamespace(modifiedStreamId.finalNamespace());
    }
  }

  /**
   * Verify column names that are reserved keywords are handled successfully. Each destination should
   * always have at least 1 column in the record data that is a reserved keyword.
   */
  @Test
  public void testReservedKeywords() throws Exception {
    createRawTable(streamId);
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/reservedkeywords_inputrecords_raw.jsonl"));
    final StreamConfig stream = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND,
        null,
        Optional.empty(),
        new LinkedHashMap<>() {

          {
            put(generator.buildColumnId("current_date"), AirbyteProtocolType.STRING);
            put(generator.buildColumnId("join"), AirbyteProtocolType.STRING);
          }

        });

    final String createTable = generator.createTable(stream, "", false);
    destinationHandler.execute(createTable);
    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, stream, Optional.empty(), "");

    DIFFER.diffFinalTableRecords(
        BaseTypingDedupingTest.readRecords("sqlgenerator/reservedkeywords_expectedrecords_final.jsonl"),
        dumpFinalTableRecords(streamId, ""));
  }

  /**
   * Verify that the final table does not include NON-NULL PKs (after
   * https://github.com/airbytehq/airbyte/pull/31082)
   */
  @Test
  public void ensurePKsAreIndexedUnique() throws Exception {
    createRawTable(streamId);
    insertRawTableRecords(
        streamId,
        List.of(Jsons.deserialize(
            """
            {
              "_airbyte_raw_id": "14ba7c7f-e398-4e69-ac22-28d578400dbc",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_data": {
                "id1": 1,
                "id2": 2
              }
            }
            """)));

    final String createTable = generator.createTable(incrementalDedupStream, "", false);

    // should be OK with new tables
    destinationHandler.execute(createTable);
    final Optional<DialectTableDefinition> existingTableA = destinationHandler.findExistingTable(streamId);
    assertTrue(generator.existingSchemaMatchesStreamConfig(incrementalDedupStream, existingTableA.get()));
    destinationHandler.execute("DROP TABLE " + streamId.finalTableId(""));

    // Hack the create query to add NOT NULLs to emulate the old behavior
    final String createTableModified = Arrays.stream(createTable.split(System.lineSeparator()))
        .map(line -> !line.contains("CLUSTER") && (line.contains("id1") || line.contains("id2") || line.contains("ID1") || line.contains("ID2"))
            ? line.replace(",", " NOT NULL,")
            : line)
        .collect(Collectors.joining("\r\n"));
    destinationHandler.execute(createTableModified);
    final Optional<DialectTableDefinition> existingTableB = destinationHandler.findExistingTable(streamId);
    assertFalse(generator.existingSchemaMatchesStreamConfig(incrementalDedupStream, existingTableB.get()));
  }

  /**
   * A stream with no columns is weird, but we shouldn't treat it specially in any way. It should
   * create a final table as usual, and populate it with the relevant metadata columns.
   */
  @Test
  public void noColumns() throws Exception {
    createRawTable(streamId);
    insertRawTableRecords(
        streamId,
        List.of(Jsons.deserialize(
            """
            {
              "_airbyte_raw_id": "14ba7c7f-e398-4e69-ac22-28d578400dbc",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_data": {}
            }
            """)));
    final StreamConfig stream = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND,
        emptyList(),
        Optional.empty(),
        new LinkedHashMap<>());

    final String createTable = generator.createTable(stream, "", false);
    destinationHandler.execute(createTable);
    TypeAndDedupeTransaction.executeTypeAndDedupe(generator, destinationHandler, stream, Optional.empty(), "");

    verifyRecords(
        "sqlgenerator/nocolumns_expectedrecords_raw.jsonl",
        dumpRawTableRecords(streamId),
        "sqlgenerator/nocolumns_expectedrecords_final.jsonl",
        dumpFinalTableRecords(streamId, ""));
  }

  @Test
  public void testV1V2migration() throws Exception {
    // This is maybe a little hacky, but it avoids having to refactor this entire class and subclasses
    // for something that is going away
    final StreamId v1RawTableStreamId = new StreamId(null, null, streamId.finalNamespace(), "v1_" + streamId.rawName(), null, null);
    createV1RawTable(v1RawTableStreamId);
    insertV1RawTableRecords(v1RawTableStreamId, BaseTypingDedupingTest.readRecords(
        "sqlgenerator/all_types_v1_inputrecords.jsonl"));
    final String migration = generator.migrateFromV1toV2(streamId, v1RawTableStreamId.rawNamespace(), v1RawTableStreamId.rawName());
    destinationHandler.execute(migration);
    final List<JsonNode> v1RawRecords = dumpV1RawTableRecords(v1RawTableStreamId);
    final List<JsonNode> v2RawRecords = dumpRawTableRecords(streamId);
    migrationAssertions(v1RawRecords, v2RawRecords);
  }

  /**
   * Sometimes, a sync doesn't delete its soft reset temp table. (it's not entirely clear why this
   * happens.) In these cases, the next sync should not crash.
   */
  @Test
  public void softResetIgnoresPreexistingTempTable() throws Exception {
    createRawTable(incrementalDedupStream.id());

    // Create a soft reset table. Use incremental append mode, in case the destination connector uses
    // different
    // indexing/partitioning/etc.
    final String createOldTempTable = generator.createTable(incrementalAppendStream, TypeAndDedupeTransaction.SOFT_RESET_SUFFIX, false);
    destinationHandler.execute(createOldTempTable);

    // Execute a soft reset. This should not crash.
    TypeAndDedupeTransaction.executeSoftReset(generator, destinationHandler, incrementalAppendStream);
  }

  protected void migrationAssertions(final List<JsonNode> v1RawRecords, final List<JsonNode> v2RawRecords) {
    final var v2RecordMap = v2RawRecords.stream().collect(Collectors.toMap(
        record -> record.get("_airbyte_raw_id").asText(),
        Function.identity()));
    assertAll(
        () -> assertEquals(5, v1RawRecords.size()),
        () -> assertEquals(5, v2RawRecords.size()));
    v1RawRecords.forEach(v1Record -> {
      final var v1id = v1Record.get("_airbyte_ab_id").asText();
      assertAll(
          () -> assertEquals(v1id, v2RecordMap.get(v1id).get("_airbyte_raw_id").asText()),
          () -> assertEquals(v1Record.get("_airbyte_emitted_at").asText(), v2RecordMap.get(v1id).get("_airbyte_extracted_at").asText()),
          () -> assertNull(v2RecordMap.get(v1id).get("_airbyte_loaded_at")));
      JsonNode originalData = v1Record.get("_airbyte_data");
      if (originalData.isTextual()) {
        originalData = Jsons.deserializeExact(originalData.asText());
      }
      JsonNode migratedData = v2RecordMap.get(v1id).get("_airbyte_data");
      if (migratedData.isTextual()) {
        migratedData = Jsons.deserializeExact(migratedData.asText());
      }
      // hacky thing because we only care about the data contents.
      // diffRawTableRecords makes some assumptions about the structure of the blob.
      DIFFER.diffFinalTableRecords(List.of(originalData), List.of(migratedData));
    });
  }

  protected List<JsonNode> dumpV1RawTableRecords(final StreamId streamId) throws Exception {
    return dumpRawTableRecords(streamId);
  }

  @Test
  public void testCreateTableForce() throws Exception {
    final String createTableNoForce = generator.createTable(incrementalDedupStream, "", false);
    final String createTableForce = generator.createTable(incrementalDedupStream, "", true);

    destinationHandler.execute(createTableNoForce);
    assertThrows(Exception.class, () -> destinationHandler.execute(createTableNoForce));
    // This should not throw an exception
    destinationHandler.execute(createTableForce);

    assertTrue(destinationHandler.findExistingTable(streamId).isPresent());
  }

  protected void createFinalTable(final StreamConfig stream, final String suffix) throws Exception {
    final String createTable = generator.createTable(stream, suffix, false);
    destinationHandler.execute(createTable);
  }

  private void verifyRecords(final String expectedRawRecordsFile,
                             final List<JsonNode> actualRawRecords,
                             final String expectedFinalRecordsFile,
                             final List<JsonNode> actualFinalRecords) {
    assertAll(
        () -> DIFFER.diffRawTableRecords(
            BaseTypingDedupingTest.readRecords(expectedRawRecordsFile),
            actualRawRecords),
        () -> assertEquals(
            0,
            actualRawRecords.stream()
                .filter(record -> !record.hasNonNull("_airbyte_loaded_at"))
                .count()),
        () -> DIFFER.diffFinalTableRecords(
            BaseTypingDedupingTest.readRecords(expectedFinalRecordsFile),
            actualFinalRecords));
  }

  private void verifyRecordCounts(final int expectedRawRecords,
                                  final List<JsonNode> actualRawRecords,
                                  final int expectedFinalRecords,
                                  final List<JsonNode> actualFinalRecords) {
    assertAll(
        () -> assertEquals(
            expectedRawRecords,
            actualRawRecords.size(),
            "Raw record count was incorrect"),
        () -> assertEquals(
            0,
            actualRawRecords.stream()
                .filter(record -> !record.hasNonNull("_airbyte_loaded_at"))
                .count()),
        () -> assertEquals(
            expectedFinalRecords,
            actualFinalRecords.size(),
            "Final record count was incorrect"));
  }

}
