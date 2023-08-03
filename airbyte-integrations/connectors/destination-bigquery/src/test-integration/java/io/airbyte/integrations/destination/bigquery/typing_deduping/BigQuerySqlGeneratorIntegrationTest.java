/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.FieldValueList;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableResult;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
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
  private static final BigQuerySqlGenerator GENERATOR = new BigQuerySqlGenerator("US");
  public static final ColumnId ID_COLUMN = GENERATOR.buildColumnId("id");
  public static final List<ColumnId> PRIMARY_KEY = List.of(ID_COLUMN);
  public static final ColumnId CURSOR = GENERATOR.buildColumnId("updated_at");
  public static final ColumnId CDC_CURSOR = GENERATOR.buildColumnId("_ab_cdc_lsn");
  public static final String QUOTE = "`";
  private static final LinkedHashMap<ColumnId, AirbyteType> COLUMNS;
  private static final LinkedHashMap<ColumnId, AirbyteType> CDC_COLUMNS;

  private static BigQuery bq;
  private static BigQueryDestinationHandler destinationHandler;

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

    CDC_COLUMNS = new LinkedHashMap<>(COLUMNS);
    CDC_COLUMNS.put(GENERATOR.buildColumnId("_ab_cdc_deleted_at"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
  }

  @BeforeAll
  public static void setup() throws Exception {
    final String rawConfig = Files.readString(Path.of("secrets/credentials-gcs-staging.json"));
    final JsonNode config = Jsons.deserialize(rawConfig);

    bq = BigQueryDestination.getBigQuery(config);
    destinationHandler = new BigQueryDestinationHandler(bq, "US");
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
  public void softReset() throws InterruptedException {
    createRawTable();
    createFinalTableCdc();
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "dataset", testDataset)).replace(
                """
                    ALTER TABLE ${dataset}.users_final ADD COLUMN `weird_new_column` INT64;

                    INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
                      (JSON'{"id": 1, "updated_at": "2023-01-01T02:00:00Z", "string": "Alice", "struct": {"city": "San Diego", "state": "CA"}, "integer": 84}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
                      (JSON'{"id": 2, "updated_at": "2023-01-01T03:00:00Z", "string": "Bob", "integer": "oops"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');
                    """))
        .build());

    final String sql = GENERATOR.softReset(incrementalDedupStreamConfig());
    destinationHandler.execute(sql);

    TableDefinition finalTableDefinition = bq.getTable(TableId.of(testDataset, "users_final")).getDefinition();
    assertTrue(
        finalTableDefinition.getSchema().getFields().stream().noneMatch(f -> f.getName().equals("weird_new_column")),
        "weird_new_column was expected to no longer exist after soft reset");
    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId(QUOTE, "")).build()).getTotalRows();
    assertEquals(2, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(2, rawRows);
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

  private StreamConfig cdcIncrementalAppendStreamConfig() {
    return new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        // This is the only difference between this and cdcStreamConfig.
        DestinationSyncMode.APPEND,
        PRIMARY_KEY,
        Optional.of(CDC_CURSOR),
        CDC_COLUMNS);
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

  /**
   * TableResult contains records in a somewhat nonintuitive format (and it avoids loading them all into memory).
   * That's annoying for us since we're working with small test data, so just pull everything into a list.
   */
  public static List<JsonNode> toJsonRecords(final TableResult result) {
    return result.streamAll().map(row -> toJson(result.getSchema(), row)).toList();
  }

  /**
   * FieldValueList stores everything internally as string (I think?) but provides conversions to more useful types.
   * This method does that conversion, using the schema to determine which type is most appropriate. Then we just dump
   * everything into a jsonnode for interop with RecordDiffer.
   */
  private static JsonNode toJson(final Schema schema, final FieldValueList row) {
    final ObjectNode json = (ObjectNode) Jsons.emptyObject();
    for (int i = 0; i < schema.getFields().size(); i++) {
      final Field field = schema.getFields().get(i);
      final FieldValue value = row.get(i);
      final JsonNode typedValue;
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
