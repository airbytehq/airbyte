/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static com.google.cloud.bigquery.LegacySQLTypeName.legacySQLTypeName;
import static java.util.stream.Collectors.joining;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.fail;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetId;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.FieldValueList;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableResult;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.destination.typing_deduping.BaseSqlGeneratorIntegrationTest;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.bigquery.BigQueryDestination;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import org.apache.commons.text.StringSubstitutor;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Execution(ExecutionMode.CONCURRENT)
public class BigQuerySqlGeneratorIntegrationTest extends BaseSqlGeneratorIntegrationTest<TableDefinition> {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQuerySqlGeneratorIntegrationTest.class);

  private static BigQuery bq;

  @BeforeAll
  public static void setupBigquery() throws Exception {
    final String rawConfig = Files.readString(Path.of("secrets/credentials-gcs-staging.json"));
    final JsonNode config = Jsons.deserialize(rawConfig);
    bq = BigQueryDestination.getBigQuery(config);
  }

  @Override
  protected BigQuerySqlGenerator getSqlGenerator() {
    return new BigQuerySqlGenerator("US");
  }

  @Override
  protected BigQueryDestinationHandler getDestinationHandler() {
    return new BigQueryDestinationHandler(bq, "US");
  }

  @Override
  protected void createNamespace(String namespace) {
    bq.create(DatasetInfo.newBuilder(namespace)
        // This unfortunately doesn't delete the actual dataset after 3 days, but at least we'll clear out old tables automatically
        .setDefaultTableLifetime(Duration.ofDays(3).toMillis())
        .build());
  }

  @Override
  protected void createRawTable(StreamId streamId) throws InterruptedException {
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "raw_table_id", streamId.rawTableId(BigQuerySqlGenerator.QUOTE))).replace(
                """
                    CREATE TABLE ${raw_table_id} (
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

  @Override
  protected void createFinalTable(boolean includeCdcDeletedAt, StreamId streamId, String suffix) throws InterruptedException {
    String cdcDeletedAt = includeCdcDeletedAt ? "`_ab_cdc_deleted_at` TIMESTAMP," : "";
    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "final_table_id", streamId.finalTableId(BigQuerySqlGenerator.QUOTE, suffix),
                "cdc_deleted_at", cdcDeletedAt)).replace(
                """
                    CREATE TABLE ${final_table_id} (
                      _airbyte_raw_id STRING NOT NULL,
                      _airbyte_extracted_at TIMESTAMP NOT NULL,
                      _airbyte_meta JSON NOT NULL,
                      `id1` INT64,
                      `id2` INT64,
                      `updated_at` TIMESTAMP,
                      ${cdc_deleted_at}
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
                    CLUSTER BY id1, id2, _airbyte_extracted_at;
                    """))
        .build());
  }

  @Override
  protected void insertFinalTableRecords(boolean includeCdcDeletedAt, StreamId streamId, String suffix, List<JsonNode> records) throws InterruptedException {
    List<String> columnNames = includeCdcDeletedAt ? FINAL_TABLE_COLUMN_NAMES_CDC : FINAL_TABLE_COLUMN_NAMES;
    String cdcDeletedAtDecl = includeCdcDeletedAt ? ",`_ab_cdc_deleted_at` TIMESTAMP" : "";
    String cdcDeletedAtName = includeCdcDeletedAt ? ",`_ab_cdc_deleted_at`" : "";
    String recordsText = records.stream()
        // For each record, convert it to a string like "(rawId, extractedAt, loadedAt, data)"
        .map(record -> columnNames.stream()
            .map(record::get)
            .map(r -> {
              if (r == null) {
                return "NULL";
              }
              String stringContents;
              if (r.isTextual()) {
                stringContents = r.asText();
              } else {
                stringContents = r.toString();
              }
              return '"' + stringContents
                  // Serialized json might contain backslashes and double quotes. Escape them.
                  .replace("\\", "\\\\")
                  .replace("\"", "\\\"") + '"';
            })
            .collect(joining(",")))
        .map(row -> "(" + row + ")")
        .collect(joining(","));

    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "final_table_id", streamId.finalTableId(BigQuerySqlGenerator.QUOTE, suffix),
                "cdc_deleted_at_name", cdcDeletedAtName,
                "cdc_deleted_at_decl", cdcDeletedAtDecl,
                "records", recordsText)).replace(
                // Similar to insertRawTableRecords, some of these columns are declared as string and wrapped in parse_json().
                // There's also a bunch of casting, because bigquery doesn't coerce strings to e.g. int
                """
                    insert into ${final_table_id} (
                      _airbyte_raw_id,
                      _airbyte_extracted_at,
                      _airbyte_meta,
                      `id1`,
                      `id2`,
                      `updated_at`,
                      `struct`,
                      `array`,
                      `string`,
                      `number`,
                      `integer`,
                      `boolean`,
                      `timestamp_with_timezone`,
                      `timestamp_without_timezone`,
                      `time_with_timezone`,
                      `time_without_timezone`,
                      `date`,
                      `unknown`
                      ${cdc_deleted_at_name}
                    )
                    select
                      _airbyte_raw_id,
                      _airbyte_extracted_at,
                      parse_json(_airbyte_meta),
                      cast(`id1` as int64),
                      cast(`id2` as int64),
                      `updated_at`,
                      parse_json(`struct`),
                      parse_json(`array`),
                      `string`,
                      cast(`number` as numeric),
                      cast(`integer` as int64),
                      cast(`boolean` as boolean),
                      `timestamp_with_timezone`,
                      `timestamp_without_timezone`,
                      `time_with_timezone`,
                      `time_without_timezone`,
                      `date`,
                      parse_json(`unknown`)
                      ${cdc_deleted_at_name}
                    from unnest([
                      STRUCT<
                        _airbyte_raw_id STRING,
                        _airbyte_extracted_at TIMESTAMP,
                        _airbyte_meta STRING,
                        `id1` STRING,
                        `id2` STRING,
                        `updated_at` TIMESTAMP,
                        `struct` STRING,
                        `array` STRING,
                        `string` STRING,
                        `number` STRING,
                        `integer` STRING,
                        `boolean` STRING,
                        `timestamp_with_timezone` TIMESTAMP,
                        `timestamp_without_timezone` DATETIME,
                        `time_with_timezone` STRING,
                        `time_without_timezone` TIME,
                        `date` DATE,
                        `unknown` STRING
                        ${cdc_deleted_at_decl}
                      >
                      ${records}
                    ])
                    """))
        .build());
  }

  @Override
  protected void insertRawTableRecords(StreamId streamId, List<JsonNode> records) throws InterruptedException {
    String recordsText = records.stream()
        // For each record, convert it to a string like "(rawId, extractedAt, loadedAt, data)"
        .map(record -> JavaBaseConstants.V2_COLUMN_NAMES.stream()
            .map(record::get)
            .map(r -> {
              if (r == null) {
                return "NULL";
              }
              String stringContents;
              if (r.isTextual()) {
                stringContents = r.asText();
              } else {
                stringContents = r.toString();
              }
              return '"' + stringContents
                  // Serialized json might contain backslashes and double quotes. Escape them.
                  .replace("\\", "\\\\")
                  .replace("\"", "\\\"") + '"';
            })
            .collect(joining(",")))
        .map(row -> "(" + row + ")")
        .collect(joining(","));

    bq.query(QueryJobConfiguration.newBuilder(
            new StringSubstitutor(Map.of(
                "raw_table_id", streamId.rawTableId(BigQuerySqlGenerator.QUOTE),
                "records", recordsText)).replace(
                // Note the parse_json call, and that _airbyte_data is declared as a string.
                // This is needed because you can't insert a string literal into a JSON column
                // so we build a struct literal with a string field, and then parse the field when inserting to the table.
                """
                    INSERT INTO ${raw_table_id} (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_loaded_at, _airbyte_data)
                    SELECT _airbyte_raw_id, _airbyte_extracted_at, _airbyte_loaded_at, parse_json(_airbyte_data) FROM UNNEST([
                      STRUCT<`_airbyte_raw_id` STRING, `_airbyte_extracted_at` TIMESTAMP, `_airbyte_loaded_at` TIMESTAMP, _airbyte_data STRING>
                      ${records}
                    ])
                    """))
        .build());
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(StreamId streamId) throws Exception {
    TableResult result = bq.query(QueryJobConfiguration.of("SELECT * FROM " + streamId.rawTableId(BigQuerySqlGenerator.QUOTE)));
    return BigQuerySqlGeneratorIntegrationTest.toJsonRecords(result);
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(StreamId streamId, String suffix) throws Exception {
    TableResult result = bq.query(QueryJobConfiguration.of("SELECT * FROM " + streamId.finalTableId(BigQuerySqlGenerator.QUOTE, suffix)));
    return BigQuerySqlGeneratorIntegrationTest.toJsonRecords(result);
  }

  @Override
  protected void teardownNamespace(String namespace) {
    bq.delete(namespace, BigQuery.DatasetDeleteOption.deleteContents());
  }

  @Override
  @Test
  public void testCreateTableIncremental() throws Exception {
    destinationHandler.execute(generator.createTable(incrementalDedupStream, ""));

    final Table table = bq.getTable(namespace, "users_final");
    // The table should exist
    assertNotNull(table);
    final Schema schema = table.getDefinition().getSchema();
    // And we should know exactly what columns it contains
    assertEquals(
        // Would be nice to assert directly against StandardSQLTypeName, but bigquery returns schemas of
        // LegacySQLTypeName. So we have to translate.
        Schema.of(
            Field.newBuilder("_airbyte_raw_id", legacySQLTypeName(StandardSQLTypeName.STRING)).setMode(Field.Mode.REQUIRED).build(),
            Field.newBuilder("_airbyte_extracted_at", legacySQLTypeName(StandardSQLTypeName.TIMESTAMP)).setMode(Field.Mode.REQUIRED).build(),
            Field.newBuilder("_airbyte_meta", legacySQLTypeName(StandardSQLTypeName.JSON)).setMode(Field.Mode.REQUIRED).build(),
            Field.of("id1", legacySQLTypeName(StandardSQLTypeName.INT64)),
            Field.of("id2", legacySQLTypeName(StandardSQLTypeName.INT64)),
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
  public void testCreateTableInOtherRegion() throws InterruptedException {
    BigQueryDestinationHandler destinationHandler = new BigQueryDestinationHandler(bq, "asia-east1");
    // We're creating the dataset in the wrong location in the @BeforeEach block. Explicitly delete it.
    bq.getDataset(namespace).delete();

    destinationHandler.execute(new BigQuerySqlGenerator("asia-east1").createTable(incrementalDedupStream, ""));

    // Empirically, it sometimes takes Bigquery nearly 30 seconds to propagate the dataset's existence.
    // Give ourselves 2 minutes just in case.
    for (int i = 0; i < 120; i++) {
      final Dataset dataset = bq.getDataset(DatasetId.of(bq.getOptions().getProjectId(), namespace));
      if (dataset == null) {
        LOGGER.info("Sleeping and trying again... ({})", i);
        Thread.sleep(1000);
      } else {
        assertEquals("asia-east1", dataset.getLocation());
        return;
      }
    }
    fail("Dataset does not exist");
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
