/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Streams;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;
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

  private static final RecordDiffer DIFFER = new RecordDiffer(
      Pair.of("id1", AirbyteProtocolType.INTEGER),
      Pair.of("id2", AirbyteProtocolType.INTEGER),
      Pair.of("updated_at", AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE));

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

  private StreamId streamId;
  private List<ColumnId> primaryKey;
  private ColumnId cursor;

  protected abstract SqlGenerator<DialectTableDefinition> getSqlGenerator();

  protected abstract DestinationHandler<DialectTableDefinition> getDestinationHandler();

  /**
   * Do any setup work to create a namespace for this test run. For example, this might create a
   * BigQuery dataset, or a Snowflake schema.
   */
  protected abstract void createNamespace(String namespace);

  /**
   * Create a raw table using the StreamId's rawTableId.
   */
  protected abstract void createRawTable(StreamId streamId) throws Exception;

  /**
   * Create a final table usingi the StreamId's finalTableId. Subclasses are recommended to hardcode
   * the columns from {@link #FINAL_TABLE_COLUMN_NAMES} or {@link #FINAL_TABLE_COLUMN_NAMES_CDC}. The
   * only difference between those two column lists is the inclusion of the _ab_cdc_deleted_at column,
   * which is controlled by the includeCdcDeletedAt parameter.
   */
  protected abstract void createFinalTable(boolean includeCdcDeletedAt, StreamId streamId, String suffix) throws Exception;

  protected abstract void insertRawTableRecords(StreamId streamId, List<JsonNode> records) throws Exception;

  protected abstract void insertFinalTableRecords(boolean includeCdcDeletedAt, StreamId streamId, String suffix, List<JsonNode> records)
      throws Exception;

  /**
   * The two dump methods are defined identically as in {@link BaseTypingDedupingTest}, but with
   * slightly different method signature. This test expects subclasses to respect the raw/finalTableId
   * on the StreamId object, rather than hardcoding e.g. the airbyte_internal dataset.
   */
  protected abstract List<JsonNode> dumpRawTableRecords(StreamId streamId) throws Exception;

  protected abstract List<JsonNode> dumpFinalTableRecords(StreamId streamId, String suffix) throws Exception;

  /**
   * Clean up all resources in the namespace. For example, this might delete the BigQuery dataset
   * created in {@link #createNamespace(String)}.
   */
  protected abstract void teardownNamespace(String namespace);

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
  public void setup() {
    generator = getSqlGenerator();
    destinationHandler = getDestinationHandler();
    ColumnId id1 = generator.buildColumnId("id1");
    ColumnId id2 = generator.buildColumnId("id2");
    primaryKey = List.of(id1, id2);
    cursor = generator.buildColumnId("updated_at");

    LinkedHashMap<ColumnId, AirbyteType> columns = new LinkedHashMap<>();
    columns.put(id1, AirbyteProtocolType.INTEGER);
    columns.put(id2, AirbyteProtocolType.INTEGER);
    columns.put(cursor, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    columns.put(generator.buildColumnId("struct"), new Struct(new LinkedHashMap<>()));
    columns.put(generator.buildColumnId("array"), new Array(AirbyteProtocolType.UNKNOWN));
    columns.put(generator.buildColumnId("string"), AirbyteProtocolType.STRING);
    columns.put(generator.buildColumnId("number"), AirbyteProtocolType.NUMBER);
    columns.put(generator.buildColumnId("integer"), AirbyteProtocolType.INTEGER);
    columns.put(generator.buildColumnId("boolean"), AirbyteProtocolType.BOOLEAN);
    columns.put(generator.buildColumnId("timestamp_with_timezone"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    columns.put(generator.buildColumnId("timestamp_without_timezone"), AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE);
    columns.put(generator.buildColumnId("time_with_timezone"), AirbyteProtocolType.TIME_WITH_TIMEZONE);
    columns.put(generator.buildColumnId("time_without_timezone"), AirbyteProtocolType.TIME_WITHOUT_TIMEZONE);
    columns.put(generator.buildColumnId("date"), AirbyteProtocolType.DATE);
    columns.put(generator.buildColumnId("unknown"), AirbyteProtocolType.UNKNOWN);

    LinkedHashMap<ColumnId, AirbyteType> cdcColumns = new LinkedHashMap<>(columns);
    cdcColumns.put(generator.buildColumnId("_ab_cdc_deleted_at"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);

    namespace = Strings.addRandomSuffix("sql_generator_test", "_", 5);
    // This is not a typical stream ID would look like, but SqlGenerator isn't allowed to make any
    // assumptions about StreamId structure.
    // In practice, the final table would be testDataset.users, and the raw table would be
    // airbyte_internal.testDataset_raw__stream_users.
    streamId = new StreamId(namespace, "users_final", namespace, "users_raw", namespace, "users_final");

    incrementalDedupStream = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        primaryKey,
        Optional.of(cursor),
        columns);
    incrementalAppendStream = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND,
        primaryKey,
        Optional.of(cursor),
        columns);

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
  public void teardown() {
    teardownNamespace(namespace);
  }

  /**
   * Test that T+D throws an error for an incremental-dedup sync where at least one record has a null
   * primary key, and that we don't write any final records.
   */
  @Test
  public void incrementalDedupInvalidPrimaryKey() throws Exception {
    createRawTable(streamId);
    createFinalTable(false, streamId, "");
    insertRawTableRecords(
        streamId,
        List.of(
            Jsons.deserialize(
                """
                {
                  "_airbyte_raw_id": "10d6e27d-ae7a-41b5-baf8-c4c277ef9c11",
                  "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                  "_airbyte_data": {}
                }
                """),
            Jsons.deserialize(
                """
                {
                  "_airbyte_raw_id": "5ce60e70-98aa-4fe3-8159-67207352c4f0",
                  "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                  "_airbyte_data": {"id1": 1, "id2": 100}
                }
                """)));

    String sql = generator.updateTable(incrementalDedupStream, "");
    assertThrows(
        Exception.class,
        () -> destinationHandler.execute(sql));
    DIFFER.diffFinalTableRecords(
        emptyList(),
        dumpFinalTableRecords(streamId, ""));
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
    createFinalTable(false, streamId, "_foo");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/alltypes_inputrecords.jsonl"));

    String sql = generator.updateTable(incrementalDedupStream, "_foo");
    destinationHandler.execute(sql);

    verifyRecords(
        "sqlgenerator/alltypes_expectedrecords_raw.jsonl",
        dumpRawTableRecords(streamId),
        "sqlgenerator/alltypes_expectedrecords_final.jsonl",
        dumpFinalTableRecords(streamId, "_foo"));
  }

  @Test
  public void incrementalDedup() throws Exception {
    createRawTable(streamId);
    createFinalTable(false, streamId, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/incrementaldedup_inputrecords.jsonl"));

    String sql = generator.updateTable(incrementalDedupStream, "");
    destinationHandler.execute(sql);

    verifyRecords(
        "sqlgenerator/incrementaldedup_expectedrecords_raw.jsonl",
        dumpRawTableRecords(streamId),
        "sqlgenerator/incrementaldedup_expectedrecords_final.jsonl",
        dumpFinalTableRecords(streamId, ""));
  }

  @Test
  public void incrementalAppend() throws Exception {
    createRawTable(streamId);
    createFinalTable(false, streamId, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/incrementaldedup_inputrecords.jsonl"));

    String sql = generator.updateTable(incrementalAppendStream, "");
    destinationHandler.execute(sql);

    verifyRecordCounts(
        3,
        dumpRawTableRecords(streamId),
        3,
        dumpFinalTableRecords(streamId, ""));
  }

  @Test
  public void overwriteFinalTable() throws Exception {
    createFinalTable(false, streamId, "_tmp");
    List<JsonNode> records = singletonList(Jsons.deserialize(
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

    DIFFER.diffFinalTableRecords(
        records,
        dumpFinalTableRecords(streamId, ""));
  }

  @Test
  public void cdcImmediateDeletion() throws Exception {
    createRawTable(streamId);
    createFinalTable(true, streamId, "");
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

    final String sql = generator.updateTable(cdcIncrementalDedupStream, "");
    destinationHandler.execute(sql);

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
    createFinalTable(true, streamId, "");
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

    final String sql = generator.updateTable(cdcIncrementalAppendStream, "");
    // Execute T+D twice
    destinationHandler.execute(sql);
    destinationHandler.execute(sql);

    verifyRecordCounts(
        1,
        dumpRawTableRecords(streamId),
        1,
        dumpFinalTableRecords(streamId, ""));
  }

  @Test
  public void cdcComplexUpdate() throws Exception {
    createRawTable(streamId);
    createFinalTable(true, streamId, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/cdcupdate_inputrecords_raw.jsonl"));
    insertFinalTableRecords(
        true,
        streamId,
        "",
        BaseTypingDedupingTest.readRecords("sqlgenerator/cdcupdate_inputrecords_final.jsonl"));

    final String sql = generator.updateTable(cdcIncrementalDedupStream, "");
    destinationHandler.execute(sql);

    verifyRecordCounts(
        // We keep the newest raw record per PK
        6,
        dumpRawTableRecords(streamId),
        4,
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
    createFinalTable(true, streamId, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/cdcordering_updateafterdelete_inputrecords.jsonl"));

    final String sql = generator.updateTable(cdcIncrementalDedupStream, "");
    destinationHandler.execute(sql);

    verifyRecordCounts(
        1,
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
    createFinalTable(true, streamId, "");
    insertRawTableRecords(
        streamId,
        BaseTypingDedupingTest.readRecords("sqlgenerator/cdcordering_insertafterdelete_inputrecords_raw.jsonl"));
    insertFinalTableRecords(
        true,
        streamId,
        "",
        BaseTypingDedupingTest.readRecords("sqlgenerator/cdcordering_insertafterdelete_inputrecords_final.jsonl"));

    final String sql = generator.updateTable(cdcIncrementalDedupStream, "");
    destinationHandler.execute(sql);

    verifyRecordCounts(
        1,
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
    createFinalTable(true, streamId, "");
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

    final String sql = generator.softReset(incrementalAppendStream);
    destinationHandler.execute(sql);

    List<JsonNode> actualRawRecords = dumpRawTableRecords(streamId);
    List<JsonNode> actualFinalRecords = dumpFinalTableRecords(streamId, "");
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
    StreamConfig stream = new StreamConfig(
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
          }

        });

    String createTable = generator.createTable(stream, "");
    destinationHandler.execute(createTable);
    final String updateTable = generator.updateTable(stream, "");
    destinationHandler.execute(updateTable);

    verifyRecords(
        "sqlgenerator/weirdcolumnnames_expectedrecords_raw.jsonl",
        dumpRawTableRecords(streamId),
        "sqlgenerator/weirdcolumnnames_expectedrecords_final.jsonl",
        dumpFinalTableRecords(streamId, ""));
  }

  private void verifyRecords(String expectedRawRecordsFile,
                             List<JsonNode> actualRawRecords,
                             String expectedFinalRecordsFile,
                             List<JsonNode> actualFinalRecords) {
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

  private void verifyRecordCounts(int expectedRawRecords,
                                  List<JsonNode> actualRawRecords,
                                  int expectedFinalRecords,
                                  List<JsonNode> actualFinalRecords) {
    assertAll(
        () -> assertEquals(
            expectedRawRecords,
            actualRawRecords.size()),
        () -> assertEquals(
            0,
            actualRawRecords.stream()
                .filter(record -> !record.hasNonNull("_airbyte_loaded_at"))
                .count()),
        () -> assertEquals(
            expectedFinalRecords,
            actualFinalRecords.size()));
  }

}
