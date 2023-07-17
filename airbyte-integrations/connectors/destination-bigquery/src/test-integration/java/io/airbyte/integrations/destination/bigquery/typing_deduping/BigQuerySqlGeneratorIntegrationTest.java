/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static com.google.cloud.bigquery.LegacySQLTypeName.legacySQLTypeName;
import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Field.Mode;
import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.FieldValueList;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableResult;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.RecordDiffer;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.bigquery.BigQueryDestination;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.apache.commons.lang3.tuple.Pair;
import org.apache.commons.text.StringSubstitutor;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// TODO write test case for multi-column PK
@Execution(ExecutionMode.CONCURRENT)
public class BigQuerySqlGeneratorIntegrationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQuerySqlGeneratorIntegrationTest.class);
  private static final BigQuerySqlGenerator GENERATOR = new BigQuerySqlGenerator();
  public static final ColumnId ID_COLUMN = GENERATOR.buildColumnId("id");
  public static final List<ColumnId> PRIMARY_KEY = List.of(ID_COLUMN);
  public static final ColumnId CURSOR = GENERATOR.buildColumnId("updated_at");
  public static final ColumnId CDC_CURSOR = GENERATOR.buildColumnId("_ab_cdc_lsn");
  public static final RecordDiffer DIFFER = new RecordDiffer(
      Pair.of("id", AirbyteProtocolType.INTEGER),
      Pair.of("updated_at", AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE),
      Pair.of("_ab_cdc_lsn", AirbyteProtocolType.INTEGER)
  );
  public static final String QUOTE = "`";
  private static final LinkedHashMap<ColumnId, AirbyteType> COLUMNS;
  private static final LinkedHashMap<ColumnId, AirbyteType> CDC_COLUMNS;

  private static BigQuery bq;

  private String testDataset;
  private StreamId streamId;

  static {
    COLUMNS = new LinkedHashMap<>();
    COLUMNS.put(ID_COLUMN, AirbyteProtocolType.INTEGER);
    COLUMNS.put(CURSOR, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    COLUMNS.put(GENERATOR.buildColumnId("struct"), new Struct(new LinkedHashMap<>()));
    COLUMNS.put(GENERATOR.buildColumnId("array"), new Array(AirbyteProtocolType.UNKNOWN));
    COLUMNS.put(GENERATOR.buildColumnId("string"), AirbyteProtocolType.STRING);
    COLUMNS.put(GENERATOR.buildColumnId("number"), AirbyteProtocolType.NUMBER);
    COLUMNS.put(GENERATOR.buildColumnId("integer"), AirbyteProtocolType.INTEGER);
    COLUMNS.put(GENERATOR.buildColumnId("boolean"), AirbyteProtocolType.BOOLEAN);
    COLUMNS.put(GENERATOR.buildColumnId("timestamp_with_timezone"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    COLUMNS.put(GENERATOR.buildColumnId("timestamp_without_timezone"), AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE);
    COLUMNS.put(GENERATOR.buildColumnId("time_with_timezone"), AirbyteProtocolType.TIME_WITH_TIMEZONE);
    COLUMNS.put(GENERATOR.buildColumnId("time_without_timezone"), AirbyteProtocolType.TIME_WITHOUT_TIMEZONE);
    COLUMNS.put(GENERATOR.buildColumnId("date"), AirbyteProtocolType.DATE);
    COLUMNS.put(GENERATOR.buildColumnId("unknown"), AirbyteProtocolType.UNKNOWN);

    CDC_COLUMNS = new LinkedHashMap<>();
    CDC_COLUMNS.put(ID_COLUMN, AirbyteProtocolType.INTEGER);
    CDC_COLUMNS.put(CDC_CURSOR, AirbyteProtocolType.INTEGER);
    CDC_COLUMNS.put(GENERATOR.buildColumnId("_ab_cdc_deleted_at"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    CDC_COLUMNS.put(GENERATOR.buildColumnId("struct"), new Struct(new LinkedHashMap<>()));
    CDC_COLUMNS.put(GENERATOR.buildColumnId("array"), new Array(AirbyteProtocolType.UNKNOWN));
    CDC_COLUMNS.put(GENERATOR.buildColumnId("string"), AirbyteProtocolType.STRING);
    CDC_COLUMNS.put(GENERATOR.buildColumnId("number"), AirbyteProtocolType.NUMBER);
    CDC_COLUMNS.put(GENERATOR.buildColumnId("integer"), AirbyteProtocolType.INTEGER);
    CDC_COLUMNS.put(GENERATOR.buildColumnId("boolean"), AirbyteProtocolType.BOOLEAN);
    CDC_COLUMNS.put(GENERATOR.buildColumnId("timestamp_with_timezone"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    CDC_COLUMNS.put(GENERATOR.buildColumnId("timestamp_without_timezone"), AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE);
    CDC_COLUMNS.put(GENERATOR.buildColumnId("time_with_timezone"), AirbyteProtocolType.TIME_WITH_TIMEZONE);
    CDC_COLUMNS.put(GENERATOR.buildColumnId("time_without_timezone"), AirbyteProtocolType.TIME_WITHOUT_TIMEZONE);
    CDC_COLUMNS.put(GENERATOR.buildColumnId("date"), AirbyteProtocolType.DATE);
    CDC_COLUMNS.put(GENERATOR.buildColumnId("unknown"), AirbyteProtocolType.UNKNOWN);
  }

  @BeforeAll
  public static void setup() throws Exception {
    String rawConfig = Files.readString(Path.of("secrets/credentials-gcs-staging.json"));
    JsonNode config = Jsons.deserialize(rawConfig);

    bq = BigQueryDestination.getBigQuery(config);
  }

  @BeforeEach
  public void setupDataset() {
    testDataset = "bq_sql_generator_test_" + UUID.randomUUID().toString().replace("-", "_");
    // This is not a typical stream ID would look like, but we're just using this to isolate our tests
    // to a specific dataset.
    // In practice, the final table would be testDataset.users, and the raw table would be
    // airbyte.testDataset_users.
    streamId = new StreamId(testDataset, "users_final", testDataset, "users_raw", testDataset, "users_final");
    LOGGER.info("Running in dataset {}", testDataset);

    bq.create(DatasetInfo.newBuilder(testDataset)
        // This unfortunately doesn't delete the actual dataset after 3 days, but at least we can clear out
        // the tables if the AfterEach is skipped.
        .setDefaultTableLifetime(Duration.ofDays(3).toMillis())
        .build());
  }

  @AfterEach
  public void teardownDataset() {
    bq.delete(testDataset, BigQuery.DatasetDeleteOption.deleteContents());
  }

  @Test
  public void testCreateTableIncremental() throws InterruptedException {
    StreamConfig stream = incrementalDedupStreamConfig();

    logAndExecute(GENERATOR.createTable(stream, ""));

    final Table table = bq.getTable(testDataset, "users_final");
    // The table should exist
    assertNotNull(table);
    final Schema schema = table.getDefinition().getSchema();
    // And we should know exactly what columns it contains
    assertEquals(
        // Would be nice to assert directly against StandardSQLTypeName, but bigquery returns schemas of
        // LegacySQLTypeName. So we have to translate.
        Schema.of(
            Field.newBuilder("_airbyte_raw_id", legacySQLTypeName(StandardSQLTypeName.STRING)).setMode(Mode.REQUIRED).build(),
            Field.newBuilder("_airbyte_extracted_at", legacySQLTypeName(StandardSQLTypeName.TIMESTAMP)).setMode(Mode.REQUIRED).build(),
            Field.newBuilder("_airbyte_meta", legacySQLTypeName(StandardSQLTypeName.JSON)).setMode(Mode.REQUIRED).build(),
            Field.of("id", legacySQLTypeName(StandardSQLTypeName.INT64)),
            Field.of("updated_at", legacySQLTypeName(StandardSQLTypeName.TIMESTAMP)),
            Field.of("struct", legacySQLTypeName(StandardSQLTypeName.JSON)),
            Field.of("array", legacySQLTypeName(StandardSQLTypeName.JSON)),
            Field.of("string", legacySQLTypeName(StandardSQLTypeName.STRING)),
            Field.of("number", legacySQLTypeName(StandardSQLTypeName.NUMERIC)),
            Field.of("integer", legacySQLTypeName(StandardSQLTypeName.INT64)),
            Field.of("boolean", legacySQLTypeName(StandardSQLTypeName.BOOL)),
            Field.of("timestamp_with_timezone", legacySQLTypeName(StandardSQLTypeName.TIMESTAMP)),
            Field.of("timestamp_without_timezone", legacySQLTypeName(StandardSQLTypeName.DATETIME)),
            Field.of("time_with_timezone", legacySQLTypeName(StandardSQLTypeName.STRING)),
            Field.of("time_without_timezone", legacySQLTypeName(StandardSQLTypeName.TIME)),
            Field.of("date", legacySQLTypeName(StandardSQLTypeName.DATE)),
            Field.of("unknown", legacySQLTypeName(StandardSQLTypeName.JSON))),
        schema);
    // TODO this should assert partitioning/clustering configs
  }

  @Test
  public void testVerifyPrimaryKeysIncremental() throws InterruptedException {
    createRawTable();
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
                      (JSON'{}', '10d6e27d-ae7a-41b5-baf8-c4c277ef9c11', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 1}', '5ce60e70-98aa-4fe3-8159-67207352c4f0', '2023-01-01T00:00:00Z');
                    """))
        .build());

    // This variable is declared outside of the transaction, so we need to do it manually here
    final String sql = "DECLARE missing_pk_count INT64;" + GENERATOR.validatePrimaryKeys(streamId, List.of(new ColumnId("id", "id", "id")), COLUMNS);
    final BigQueryException e = assertThrows(
        BigQueryException.class,
        () -> logAndExecute(sql));

    assertTrue(e.getError().getMessage().startsWith("Raw table has 1 rows missing a primary key at"),
        "Message was actually: " + e.getError().getMessage());
  }

  @Test
  public void testInsertNewRecordsIncremental() throws InterruptedException {
    createRawTable();
    createFinalTable();
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
                      (JSON'{"id": 1, "updated_at": "2023-01-01T01:00:00Z", "string": "Alice", "struct": {"city": "San Francisco", "state": "CA"}}', '972fa08a-aa06-4b91-a6af-a371aee4cb1c', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 1, "updated_at": "2023-01-01T02:00:00Z", "string": "Alice", "struct": {"city": "San Diego", "state": "CA"}}', '233ad43d-de50-4a47-bbe6-7a417ce60d9d', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 2, "updated_at": "2023-01-01T03:00:00Z", "string": "Bob", "integer": "oops"}', 'd4aeb036-2d95-4880-acd2-dc69b42b03c6', '2023-01-01T00:00:00Z');
                    """))
        .build());

    final String sql = GENERATOR.insertNewRecords(streamId, "", COLUMNS, DestinationSyncMode.OVERWRITE);
    logAndExecute(sql);

    final TableResult result = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId(QUOTE)).build());
    DIFFER.diffFinalTableRecords(
        List.of(
            Jsons.deserialize(
                """
                    {
                      "id": 1,
                      "updated_at": "2023-01-01T01:00:00Z",
                      "string": "Alice",
                      "struct": {"city": "San Francisco", "state": "CA"},
                      "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                      "_airbyte_meta": {"errors":[]}
                    }
                    """
            ),
            Jsons.deserialize(
                """
                    {
                      "id": 1,
                      "updated_at": "2023-01-01T02:00:00Z",
                      "string": "Alice",
                      "struct": {"city": "San Diego", "state": "CA"},
                      "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                      "_airbyte_meta": {"errors":[]}
                    }
                    """
            ),
            Jsons.deserialize(
                """
                    {
                      "id": 2,
                      "updated_at": "2023-01-01T03:00:00Z",
                      "string": "Bob",
                      "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                      "_airbyte_meta": {"errors":["Problem with `integer`"]}
                    }
                    """
            )),
        toJsonRecords(result));
  }

  @Test
  public void testDedupFinalTable() throws InterruptedException {
    createRawTable();
    createFinalTable();
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
                      (JSON'{"id": 1, "updated_at": "2023-01-01T01:00:00Z", "string": "Alice", "struct": {"city": "San Francisco", "state": "CA"}, "integer": 42}', 'd7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 1, "updated_at": "2023-01-01T02:00:00Z", "string": "Alice", "struct": {"city": "San Diego", "state": "CA"}, "integer": 84}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 2, "updated_at": "2023-01-01T03:00:00Z", "string": "Bob", "integer": "oops"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');

                    INSERT INTO ${dataset}.users_final (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta, `id`, `updated_at`, `string`, `struct`, `integer`) values
                      ('d7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z', JSON'{"errors":[]}', 1, '2023-01-01T01:00:00Z', 'Alice', JSON'{"city": "San Francisco", "state": "CA"}', 42),
                      ('80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z', JSON'{"errors":[]}', 1, '2023-01-01T02:00:00Z', 'Alice', JSON'{"city": "San Diego", "state": "CA"}', 84),
                      ('ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z', JSON'{"errors": ["blah blah integer"]}', 2, '2023-01-01T03:00:00Z', 'Bob', NULL, NULL);
                    """))
        .build());

    final String sql = GENERATOR.dedupFinalTable(streamId, "", PRIMARY_KEY, CURSOR);
    logAndExecute(sql);

    final TableResult result = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId(QUOTE)).build());
    DIFFER.diffFinalTableRecords(
        List.of(
            Jsons.deserialize(
                """
                    {
                      "id": 1,
                      "updated_at": "2023-01-01T02:00:00Z",
                      "string": "Alice",
                      "struct": {"city": "San Diego", "state": "CA"},
                      "integer": 84,
                      "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                      "_airbyte_meta": {"errors":[]}
                    }
                    """),
            Jsons.deserialize(
                """
                    {
                      "id": 2,
                      "updated_at": "2023-01-01T03:00:00Z",
                      "string": "Bob",
                      "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                      "_airbyte_meta": {"errors":["blah blah integer"]}
                    }
                    """)),
        toJsonRecords(result));
  }

  @Test
  public void testDedupRawTable() throws InterruptedException {
    createRawTable();
    createFinalTable();
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
                      (JSON'{"id": 1, "updated_at": "2023-01-01T01:00:00Z", "string": "Alice", "struct": {"city": "San Francisco", "state": "CA"}, "integer": 42}', 'd7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 1, "updated_at": "2023-01-01T02:00:00Z", "string": "Alice", "struct": {"city": "San Diego", "state": "CA"}, "integer": 84}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 2, "updated_at": "2023-01-01T03:00:00Z", "string": "Bob", "integer": "oops"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');

                    INSERT INTO ${dataset}.users_final (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta, `id`, `updated_at`, `string`, `struct`, `integer`) values
                      ('80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z', JSON'{"errors":[]}', 1, '2023-01-01T02:00:00Z', 'Alice', JSON'{"city": "San Diego", "state": "CA"}', 84),
                      ('ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z', JSON'{"errors": ["blah blah integer"]}', 2, '2023-01-01T03:00:00Z', 'Bob', NULL, NULL);
                    """))
        .build());

    final String sql = GENERATOR.dedupRawTable(streamId, "");
    logAndExecute(sql);

    final TableResult result = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build());
    DIFFER.diffRawTableRecords(
        List.of(
            Jsons.deserialize(
                """
                    {
                      "_airbyte_raw_id": "80c99b54-54b4-43bd-b51b-1f67dafa2c52",
                      "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                      "_airbyte_data": {"id": 1, "updated_at": "2023-01-01T02:00:00Z", "string": "Alice", "struct": {"city": "San Diego", "state": "CA"}, "integer": 84}
                    }
                    """
            ),
            Jsons.deserialize(
                """
                    {
                      "_airbyte_raw_id": "ad690bfb-c2c2-4172-bd73-a16c86ccbb67",
                      "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                      "_airbyte_data": {"id": 2, "updated_at": "2023-01-01T03:00:00Z", "string": "Bob", "integer": "oops"}
                    }
                    """
            )),
        toJsonRecords(result));
  }

  @Test
  public void testCommitRawTable() throws InterruptedException {
    createRawTable();
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
                      (JSON'{"id": 1, "updated_at": "2023-01-01T02:00:00Z", "string": "Alice", "struct": {"city": "San Diego", "state": "CA"}, "integer": 84}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 2, "updated_at": "2023-01-01T03:00:00Z", "string": "Bob", "integer": "oops"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');
                    """))
        .build());

    final String sql = GENERATOR.commitRawTable(streamId);
    logAndExecute(sql);

    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  @Test
  public void testFullUpdateAllTypes() throws InterruptedException {
    createRawTable();
    createFinalTable("_foo");
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    INSERT INTO ${dataset}.users_raw (`_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_data`) VALUES
                      (generate_uuid(), '2023-01-01T00:00:00Z', JSON'{"id": 1, "updated_at": "2023-01-01T01:00:00Z", "array": ["foo"], "struct": {"foo": "bar"}, "string": "foo", "number": 42.1, "integer": 42, "boolean": true, "timestamp_with_timezone": "2023-01-23T12:34:56Z", "timestamp_without_timezone": "2023-01-23T12:34:56", "time_with_timezone": "12:34:56Z", "time_without_timezone": "12:34:56", "date": "2023-01-23", "unknown": {}}'),
                      (generate_uuid(), '2023-01-01T00:00:00Z', JSON'{"id": 2, "updated_at": "2023-01-01T01:00:00Z", "array": null, "struct": null, "string": null, "number": null, "integer": null, "boolean": null, "timestamp_with_timezone": null, "timestamp_without_timezone": null, "time_with_timezone": null, "time_without_timezone": null, "date": null, "unknown": null}'),
                      (generate_uuid(), '2023-01-01T00:00:00Z', JSON'{"id": 3, "updated_at": "2023-01-01T01:00:00Z"}'),
                      (generate_uuid(), '2023-01-01T00:00:00Z', JSON'{"id": 4, "updated_at": "2023-01-01T01:00:00Z", "array": {}, "struct": [], "string": {}, "number": {}, "integer": {}, "boolean": {}, "timestamp_with_timezone": {}, "timestamp_without_timezone": {}, "time_with_timezone": {}, "time_without_timezone": {}, "date": {}, "unknown": null}');
                    """))
        .build());

    final String sql = GENERATOR.updateTable("_foo", incrementalDedupStreamConfig());
    logAndExecute(sql);

    final TableResult finalTable = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("_foo", QUOTE)).build());
    DIFFER.diffFinalTableRecords(
        List.of(
            Jsons.deserialize(
                """
                {
                  "id": 1,
                  "updated_at": "2023-01-01T01:00:00Z",
                  "array": ["foo"],
                  "struct": {"foo": "bar"},
                  "string": "foo",
                  "number": 42.1,
                  "integer": 42,
                  "boolean": true,
                  "timestamp_with_timezone": "2023-01-23T12:34:56Z",
                  "timestamp_without_timezone": "2023-01-23T12:34:56",
                  "time_with_timezone": "12:34:56Z",
                  "time_without_timezone": "12:34:56",
                  "date": "2023-01-23",
                  "unknown": {},
                  "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                  "_airbyte_meta": {"errors": []}
                }
                """),
            Jsons.deserialize(
                """
                {
                  "id": 2,
                  "updated_at": "2023-01-01T01:00:00Z",
                  "unknown": null,
                  "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                  "_airbyte_meta": {"errors": []}
                }
                """),
            Jsons.deserialize(
                """
                {
                  "id": 3,
                  "updated_at": "2023-01-01T01:00:00Z",
                  "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                  "_airbyte_meta": {"errors": []}
                }
                """),
            Jsons.deserialize(
                """
                {
                  "id": 4,
                  "updated_at": "2023-01-01T01:00:00Z",
                  "unknown": null,
                  "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                  "_airbyte_meta": {
                    "errors": [
                      "Problem with `struct`",
                      "Problem with `array`",
                      "Problem with `string`",
                      "Problem with `number`",
                      "Problem with `integer`",
                      "Problem with `boolean`",
                      "Problem with `timestamp_with_timezone`",
                      "Problem with `timestamp_without_timezone`",
                      "Problem with `time_with_timezone`",
                      "Problem with `time_without_timezone`",
                      "Problem with `date`"
                    ]
                  }
                }
                """)),
        toJsonRecords(finalTable));

    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(4, rawRows);
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  @Test
  public void testFullUpdateIncrementalDedup() throws InterruptedException {
    createRawTable();
    createFinalTable();
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
                      (JSON'{"id": 1, "updated_at": "2023-01-01T01:00:00Z", "string": "Alice", "struct": {"city": "San Francisco", "state": "CA"}, "integer": 42}', 'd7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 1, "updated_at": "2023-01-01T02:00:00Z", "string": "Alice", "struct": {"city": "San Diego", "state": "CA"}, "integer": 84}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 2, "updated_at": "2023-01-01T03:00:00Z", "string": "Bob", "integer": "oops"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');
                    """))
        .build());

    final String sql = GENERATOR.updateTable("", incrementalDedupStreamConfig());
    logAndExecute(sql);

    // TODO
    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId(QUOTE)).build()).getTotalRows();
    assertEquals(2, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(2, rawRows);
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  @Test
  public void testFullUpdateIncrementalAppend() throws InterruptedException {
    createRawTable();
    createFinalTable("_foo");
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
                      (JSON'{"id": 1, "updated_at": "2023-01-01T01:00:00Z", "string": "Alice", "struct": {"city": "San Francisco", "state": "CA"}, "integer": 42}', 'd7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 1, "updated_at": "2023-01-01T02:00:00Z", "string": "Alice", "struct": {"city": "San Diego", "state": "CA"}, "integer": 84}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 2, "updated_at": "2023-01-01T03:00:00Z", "string": "Bob", "integer": "oops"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');
                    """))
        .build());

    final String sql = GENERATOR.updateTable("_foo", incrementalAppendStreamConfig());
    logAndExecute(sql);

    // TODO
    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("_foo", QUOTE)).build()).getTotalRows();
    assertEquals(3, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(3, rawRows);
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  // This is also effectively the full refresh overwrite test case.
  // In the overwrite case, we rely on the destination connector to tell us to write to a final table
  // with a _tmp suffix, and then call overwriteFinalTable at the end of the sync.
  @Test
  public void testFullUpdateFullRefreshAppend() throws InterruptedException {
    createRawTable();
    createFinalTable("_foo");
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
                      (JSON'{"id": 1, "updated_at": "2023-01-01T01:00:00Z", "string": "Alice", "struct": {"city": "San Francisco", "state": "CA"}, "integer": 42}', 'd7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 1, "updated_at": "2023-01-01T02:00:00Z", "string": "Alice", "struct": {"city": "San Diego", "state": "CA"}, "integer": 84}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 2, "updated_at": "2023-01-01T03:00:00Z", "string": "Bob", "integer": "oops"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');

                    INSERT INTO ${dataset}.users_final_foo (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta, `id`, `updated_at`, `string`, `struct`, `integer`) values
                      ('64f4390f-3da1-4b65-b64a-a6c67497f18d', '2022-12-31T00:00:00Z', JSON'{"errors": []}', 1, '2022-12-31T00:00:00Z', 'Alice', NULL, NULL);
                    """))
        .build());

    final String sql = GENERATOR.updateTable("_foo", fullRefreshAppendStreamConfig());
    logAndExecute(sql);

    // TODO
    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("_foo", QUOTE)).build()).getTotalRows();
    assertEquals(4, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(3, rawRows);
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  @Test
  public void testRenameFinalTable() throws InterruptedException {
    createFinalTable("_tmp");

    final String sql = GENERATOR.overwriteFinalTable("_tmp", fullRefreshOverwriteStreamConfig()).get();
    logAndExecute(sql);

    final Table table = bq.getTable(testDataset, "users_final");
    // TODO this should assert table schema + partitioning/clustering configs
    assertNotNull(table);
  }

  @Test
  public void testCdcBasics() throws InterruptedException {
    createRawTable();
    createFinalTableCdc();
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_loaded_at`) VALUES
                  (JSON'{"id": 1, "_ab_cdc_lsn": 10001, "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"}', generate_uuid(), '2023-01-01T00:00:00Z', NULL);
                """))
        .build());

    final String sql = GENERATOR.updateTable("", cdcStreamConfig());
    logAndExecute(sql);

    // TODO better asserts
    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("", QUOTE)).build()).getTotalRows();
    assertEquals(0, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(1, rawRows);
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  @Test
  public void testCdcUpdate() throws InterruptedException {
    createRawTable();
    createFinalTableCdc();
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                -- records from a previous sync
                INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_loaded_at`) VALUES
                  (JSON'{"id": 1, "_ab_cdc_lsn": 900, "string": "spooky ghost", "_ab_cdc_deleted_at": null}', '64f4390f-3da1-4b65-b64a-a6c67497f18d', '2022-12-31T00:00:00Z', '2022-12-31T00:00:01Z'),
                  (JSON'{"id": 0, "_ab_cdc_lsn": 901, "string": "zombie", "_ab_cdc_deleted_at": "2022-12-31T00:O0:00Z"}', generate_uuid(), '2022-12-31T00:00:00Z', '2022-12-31T00:00:01Z'),
                  (JSON'{"id": 5, "_ab_cdc_lsn": 902, "string": "will not be deleted", "_ab_cdc_deleted_at": null}', 'b6139181-a42c-45c3-89f2-c4b4bb3a8c9d', '2022-12-31T00:00:00Z', '2022-12-31T00:00:01Z');
                INSERT INTO ${dataset}.users_final (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta, `id`, `_ab_cdc_lsn`, `string`, `struct`, `integer`) values
                  ('64f4390f-3da1-4b65-b64a-a6c67497f18d', '2022-12-31T00:00:00Z', JSON'{}', 1, 900, 'spooky ghost', NULL, NULL),
                  ('b6139181-a42c-45c3-89f2-c4b4bb3a8c9d', '2022-12-31T00:00:00Z', JSON'{}', 5, 901, 'will be deleted', NULL, NULL);

                -- new records from the current sync
                INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
                  (JSON'{"id": 2, "_ab_cdc_lsn": 10001, "_ab_cdc_deleted_at": null, "string": "alice"}', generate_uuid(), '2023-01-01T00:00:00Z'),
                  (JSON'{"id": 2, "_ab_cdc_lsn": 10002, "_ab_cdc_deleted_at": null, "string": "alice2"}', generate_uuid(), '2023-01-01T00:00:00Z'),
                  (JSON'{"id": 3, "_ab_cdc_lsn": 10003, "_ab_cdc_deleted_at": null, "string": "bob"}', generate_uuid(), '2023-01-01T00:00:00Z'),
                  (JSON'{"id": 1, "_ab_cdc_lsn": 10004, "_ab_cdc_deleted_at": "2022-12-31T23:59:59Z"}', generate_uuid(), '2023-01-01T00:00:00Z'),
                  (JSON'{"id": 0, "_ab_cdc_lsn": 10005, "_ab_cdc_deleted_at": null, "string": "zombie_returned"}', generate_uuid(), '2023-01-01T00:00:00Z'),
                  -- CDC generally outputs an explicit null for deleted_at, but verify that we can also handle the case where deleted_at is unset.
                  (JSON'{"id": 4, "_ab_cdc_lsn": 10006, "string": "charlie"}', generate_uuid(), '2023-01-01T00:00:00Z'),
                  -- Verify that we can handle weird values in deleted_at
                  (JSON'{"id": 5, "_ab_cdc_lsn": 10007, "_ab_cdc_deleted_at": {}, "string": "david"}', generate_uuid(), '2023-01-01T00:00:00Z');
                """))
        .build());

    final String sql = GENERATOR.updateTable("", cdcStreamConfig());
    logAndExecute(sql);

    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("", QUOTE)).build()).getTotalRows();
    assertEquals(5, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(6, rawRows); // we only keep the newest raw record for reach PK
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
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
  public void testCdcOrdering_updateAfterDelete() throws InterruptedException {
    createRawTable();
    createFinalTableCdc();
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    -- Write raw deletion record from the first batch, which resulted in an empty final table.
                    -- Note the non-null loaded_at - this is to simulate that we previously ran T+D on this record.
                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_loaded_at`) VALUES
                      (JSON'{"id": 1, "_ab_cdc_lsn": 10001, "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"}', generate_uuid(), '2023-01-01T00:00:00Z', '2023-01-01T00:00:01Z');

                    -- insert raw record from the second record batch - this is an outdated record that should be ignored.
                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
                      (JSON'{"id": 1, "_ab_cdc_lsn": 10000, "string": "alice"}', generate_uuid(), '2023-01-01T00:00:00Z');
                    """))
        .build());

    final String sql = GENERATOR.updateTable("", cdcStreamConfig());
    logAndExecute(sql);

    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("", QUOTE)).build()).getTotalRows();
    assertEquals(0, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(1, rawRows);
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
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
  public void testCdcOrdering_insertAfterDelete() throws InterruptedException {
    createRawTable();
    createFinalTableCdc();
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    -- records from the first batch
                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_loaded_at`) VALUES
                      (JSON'{"id": 1, "_ab_cdc_lsn": 10002, "string": "alice_reinsert"}', '64f4390f-3da1-4b65-b64a-a6c67497f18d', '2023-01-01T00:00:00Z', '2023-01-01T00:00:01Z');
                    INSERT INTO ${dataset}.users_final (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta, `id`, `_ab_cdc_lsn`, `string`) values
                      ('64f4390f-3da1-4b65-b64a-a6c67497f18d', '2023-01-01T00:00:00Z', JSON'{}', 1, 10002, 'alice_reinsert');

                    -- second record batch
                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
                      (JSON'{"id": 1, "_ab_cdc_lsn": 10001, "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"}', generate_uuid(), '2023-01-01T00:00:00Z');
                    """))
        .build());
    // Run the second round of typing and deduping. This should do nothing to the final table, because
    // the delete is outdated.
    final String sql = GENERATOR.updateTable("", cdcStreamConfig());
    logAndExecute(sql);

    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("", QUOTE)).build()).getTotalRows();
    assertEquals(1, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(1, rawRows);
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  private StreamConfig incrementalDedupStreamConfig() {
    return new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        PRIMARY_KEY,
        Optional.of(CURSOR),
        COLUMNS);
  }

  private StreamConfig cdcStreamConfig() {
    return new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        PRIMARY_KEY,
        // Much like the rest of this class - this is purely for test purposes. Real CDC cursors may not be
        // exactly the same as this.
        Optional.of(CDC_CURSOR),
        CDC_COLUMNS);
  }

  private StreamConfig incrementalAppendStreamConfig() {
    return new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND,
        null,
        Optional.of(CURSOR),
        COLUMNS);
  }

  private StreamConfig fullRefreshAppendStreamConfig() {
    return new StreamConfig(
        streamId,
        SyncMode.FULL_REFRESH,
        DestinationSyncMode.APPEND,
        null,
        Optional.empty(),
        COLUMNS);
  }

  private StreamConfig fullRefreshOverwriteStreamConfig() {
    return new StreamConfig(
        streamId,
        SyncMode.FULL_REFRESH,
        DestinationSyncMode.OVERWRITE,
        null,
        Optional.empty(),
        COLUMNS);
  }

  // These are known-good methods for doing stuff with bigquery.
  // Some of them are identical to what the sql generator does, and that's intentional.
  private void createRawTable() throws InterruptedException {
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    CREATE TABLE ${dataset}.users_raw (
                      _airbyte_raw_id STRING NOT NULL,
                      _airbyte_data JSON NOT NULL,
                      _airbyte_extracted_at TIMESTAMP NOT NULL,
                      _airbyte_loaded_at TIMESTAMP
                    ) PARTITION BY (
                      DATE_TRUNC(_airbyte_extracted_at, DAY)
                    ) CLUSTER BY _airbyte_loaded_at;
                    """))
        .build());
  }

  private void createFinalTable() throws InterruptedException {
    createFinalTable("");
  }

  private void createFinalTable(String suffix) throws InterruptedException {
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset,
                "suffix", suffix)).replace(
                """
                    CREATE TABLE ${dataset}.users_final${suffix} (
                      _airbyte_raw_id STRING NOT NULL,
                      _airbyte_extracted_at TIMESTAMP NOT NULL,
                      _airbyte_meta JSON NOT NULL,
                      `id` INT64,
                      `updated_at` TIMESTAMP,
                      `struct` JSON,
                      `array` JSON,
                      `string` STRING,
                      `number` NUMERIC,
                      `integer` INT64,
                      `boolean` BOOL,
                      `timestamp_with_timezone` TIMESTAMP,
                      `timestamp_without_timezone` DATETIME,
                      `time_with_timezone` STRING,
                      `time_without_timezone` TIME,
                      `date` DATE,
                      `unknown` JSON
                    )
                    PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
                    CLUSTER BY id, _airbyte_extracted_at;
                    """))
        .build());
  }

  private void createFinalTableCdc() throws InterruptedException {
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    CREATE TABLE ${dataset}.users_final (
                      _airbyte_raw_id STRING NOT NULL,
                      _airbyte_extracted_at TIMESTAMP NOT NULL,
                      _airbyte_meta JSON NOT NULL,
                      `id` INT64,
                      `_ab_cdc_deleted_at` TIMESTAMP,
                      `_ab_cdc_lsn` INT64,
                      `struct` JSON,
                      `array` JSON,
                      `string` STRING,
                      `number` NUMERIC,
                      `integer` INT64,
                      `boolean` BOOL,
                      `timestamp_with_timezone` TIMESTAMP,
                      `timestamp_without_timezone` DATETIME,
                      `time_with_timezone` STRING,
                      `time_without_timezone` TIME,
                      `date` DATE,
                      `unknown` JSON
                    )
                    PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
                    CLUSTER BY id, _airbyte_extracted_at;
                    """))
        .build());
  }

  private static void logAndExecute(final String sql) throws InterruptedException {
    LOGGER.info("Executing sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());
  }

  /**
   * TableResult contains records in a somewhat nonintuitive format (and it avoids loading them all into memory).
   * That's annoying for us since we're working with small test data, so just pull everything into a list.
   */
  public static List<JsonNode> toJsonRecords(TableResult result) {
    return result.streamAll().map(row -> toJson(result.getSchema(), row)).toList();
  }

  /**
   * FieldValueList stores everything internally as string (I think?) but provides conversions to more useful types.
   * This method does that conversion, using the schema to determine which type is most appropriate. Then we just dump
   * everything into a jsonnode for interop with RecordDiffer.
   */
  private static JsonNode toJson(Schema schema, FieldValueList row) {
    final ObjectNode json = (ObjectNode) Jsons.emptyObject();
    for (int i = 0; i < schema.getFields().size(); i++) {
      final Field field = schema.getFields().get(i);
      final FieldValue value = row.get(i);
      JsonNode typedValue;
      if (!value.isNull()) {
        typedValue = switch (field.getType().getStandardType()) {
          case BOOL -> Jsons.jsonNode(value.getBooleanValue());
          case INT64 -> Jsons.jsonNode(value.getLongValue());
          case FLOAT64 -> Jsons.jsonNode(value.getDoubleValue());
          case NUMERIC, BIGNUMERIC -> Jsons.jsonNode(value.getNumericValue());
          case STRING -> Jsons.jsonNode(value.getStringValue());
          // naively converting an Instant returns a DecimalNode with the unix epoch, so instead we manually stringify it
          case TIMESTAMP -> Jsons.jsonNode(value.getTimestampInstant().toString());
          // value.getTimestampInstant() fails to parse these types
          case DATE, DATETIME, TIME -> Jsons.jsonNode(value.getStringValue());
          // bigquery returns JSON columns as string; manually parse it into a JsonNode
          case JSON -> Jsons.jsonNode(Jsons.deserialize(value.getStringValue()));

          // Default case for weird types (struct, array, geography, interval, bytes)
          default -> Jsons.jsonNode(value.getStringValue());
        };
        json.set(field.getName(), typedValue);
      }
    }
    return json;
  }

}
