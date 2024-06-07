/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static com.google.cloud.bigquery.LegacySQLTypeName.legacySQLTypeName;
import static java.util.stream.Collectors.joining;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
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
import com.google.cloud.bigquery.TableResult;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.BaseSqlGeneratorIntegrationTest;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.bigquery.BigQueryConsts;
import io.airbyte.integrations.destination.bigquery.BigQueryDestination;
import io.airbyte.integrations.destination.bigquery.migrators.BigQueryDestinationState;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.apache.commons.text.StringSubstitutor;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Execution(ExecutionMode.CONCURRENT)
public class BigQuerySqlGeneratorIntegrationTest extends BaseSqlGeneratorIntegrationTest<BigQueryDestinationState> {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQuerySqlGeneratorIntegrationTest.class);

  private static BigQuery bq;
  private static String projectId;
  private static String datasetLocation;

  @BeforeAll
  public static void setupBigquery() throws Exception {
    final String rawConfig = Files.readString(Path.of("secrets/credentials-gcs-staging.json"));
    final JsonNode config = Jsons.deserialize(rawConfig);
    bq = BigQueryDestination.getBigQuery(config);

    projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();
    datasetLocation = config.get(BigQueryConsts.CONFIG_DATASET_LOCATION).asText();
  }

  @Override
  protected BigQuerySqlGenerator getSqlGenerator() {
    return new BigQuerySqlGenerator(projectId, datasetLocation);
  }

  @Override
  protected BigQueryDestinationHandler getDestinationHandler() {
    return new BigQueryDestinationHandler(bq, "US");
  }

  @Override
  protected void createNamespace(final String namespace) {
    bq.create(DatasetInfo.newBuilder(namespace)
        // This unfortunately doesn't delete the actual dataset after 3 days, but at least we'll clear out
        // old tables automatically
        .setDefaultTableLifetime(Duration.ofDays(3).toMillis())
        .build());
  }

  @Override
  protected void createRawTable(final StreamId streamId) throws InterruptedException {
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "raw_table_id", streamId.rawTableId(BigQuerySqlGenerator.QUOTE))).replace(
                """
                CREATE TABLE ${raw_table_id} (
                  _airbyte_raw_id STRING NOT NULL,
                  _airbyte_data STRING NOT NULL,
                  _airbyte_extracted_at TIMESTAMP NOT NULL,
                  _airbyte_loaded_at TIMESTAMP,
                  _airbyte_meta STRING,
                  _airbyte_generation_id INTEGER
                ) PARTITION BY (
                  DATE_TRUNC(_airbyte_extracted_at, DAY)
                ) CLUSTER BY _airbyte_loaded_at;
                """))
        .build());
  }

  @Override
  protected void createV1RawTable(final StreamId v1RawTable) throws Exception {
    bq.query(
        QueryJobConfiguration
            .newBuilder(
                new StringSubstitutor(Map.of(
                    "raw_table_id", v1RawTable.rawTableId(BigQuerySqlGenerator.QUOTE))).replace(
                        """
                        CREATE TABLE ${raw_table_id} (
                          _airbyte_ab_id STRING NOT NULL,
                          _airbyte_data STRING NOT NULL,
                          _airbyte_emitted_at TIMESTAMP NOT NULL,
                        ) PARTITION BY (
                          DATE_TRUNC(_airbyte_emitted_at, DAY)
                        ) CLUSTER BY _airbyte_emitted_at;
                        """))
            .build());
  }

  @Override
  protected void insertFinalTableRecords(final boolean includeCdcDeletedAt,
                                         final StreamId streamId,
                                         final String suffix,
                                         final List<? extends JsonNode> records,
                                         final long generationId)
      throws InterruptedException {
    final List<String> columnNames = includeCdcDeletedAt ? FINAL_TABLE_COLUMN_NAMES_CDC : FINAL_TABLE_COLUMN_NAMES;
    final String cdcDeletedAtDecl = includeCdcDeletedAt ? ",`_ab_cdc_deleted_at` TIMESTAMP" : "";
    final String cdcDeletedAtName = includeCdcDeletedAt ? ",`_ab_cdc_deleted_at`" : "";
    final String recordsText = records.stream()
        // For each record, convert it to a string like "(rawId, extractedAt, loadedAt, data)"
        .map(record -> columnNames.stream()
            .map(record::get)
            .map(r -> {
              if (r == null) {
                return "NULL";
              }
              final String stringContents;
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
                // Similar to insertRawTableRecords, some of these columns are declared as string and wrapped in
                // parse_json().
                // There's also a bunch of casting, because bigquery doesn't coerce strings to e.g. int
                """
                insert into ${final_table_id} (
                  _airbyte_raw_id,
                  _airbyte_extracted_at,
                  _airbyte_meta,
                  _airbyte_generation_id,
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
                  _airbyte_generation_id,
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
                    _airbyte_generation_id INTEGER,
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

  private String stringifyRecords(final List<? extends JsonNode> records, final List<String> columnNames) {
    return records.stream()
        // For each record, convert it to a string like "(rawId, extractedAt, loadedAt, data)"
        .map(record -> columnNames.stream()
            .map(record::get)
            .map(r -> {
              if (r == null) {
                return "NULL";
              }
              final String stringContents;
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
  }

  @Override
  protected void insertRawTableRecords(final StreamId streamId, final List<? extends JsonNode> records) throws InterruptedException {
    final String recordsText = stringifyRecords(records, JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES_WITH_GENERATION);

    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "raw_table_id", streamId.rawTableId(BigQuerySqlGenerator.QUOTE),
            "records", recordsText)).replace(
                // TODO: Perform a normal insert - edward
                """
                INSERT INTO ${raw_table_id} (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_loaded_at, _airbyte_data, _airbyte_meta, _airbyte_generation_id)
                SELECT _airbyte_raw_id, _airbyte_extracted_at, _airbyte_loaded_at, _airbyte_data, _airbyte_meta, cast(_airbyte_generation_id as int64) FROM UNNEST([
                  STRUCT<`_airbyte_raw_id` STRING, `_airbyte_extracted_at` TIMESTAMP, `_airbyte_loaded_at` TIMESTAMP, _airbyte_data STRING, _airbyte_meta STRING, `_airbyte_generation_id` STRING>
                  ${records}
                ])
                """))
        .build());
  }

  @Override
  protected void insertV1RawTableRecords(final StreamId streamId, final List<? extends JsonNode> records) throws Exception {
    final String recordsText = stringifyRecords(records, JavaBaseConstants.LEGACY_RAW_TABLE_COLUMNS);
    bq.query(
        QueryJobConfiguration
            .newBuilder(
                new StringSubstitutor(Map.of(
                    "v1_raw_table_id", streamId.rawTableId(BigQuerySqlGenerator.QUOTE),
                    "records", recordsText)).replace(
                        """
                        INSERT INTO ${v1_raw_table_id} (_airbyte_ab_id, _airbyte_data, _airbyte_emitted_at)
                        SELECT _airbyte_ab_id, _airbyte_data, _airbyte_emitted_at FROM UNNEST([
                          STRUCT<`_airbyte_ab_id` STRING, _airbyte_data STRING, `_airbyte_emitted_at` TIMESTAMP>
                          ${records}
                        ])
                        """))
            .build());
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(final StreamId streamId) throws Exception {
    final TableResult result = bq.query(QueryJobConfiguration.of("SELECT * FROM " + streamId.rawTableId(BigQuerySqlGenerator.QUOTE)));
    return BigQuerySqlGeneratorIntegrationTest.toJsonRecords(result);
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(final StreamId streamId, final String suffix) throws Exception {
    final TableResult result = bq.query(QueryJobConfiguration.of("SELECT * FROM " + streamId.finalTableId(BigQuerySqlGenerator.QUOTE, suffix)));
    return BigQuerySqlGeneratorIntegrationTest.toJsonRecords(result);
  }

  @Override
  protected void teardownNamespace(final String namespace) {
    bq.delete(namespace, BigQuery.DatasetDeleteOption.deleteContents());
  }

  @Override
  public boolean getSupportsSafeCast() {
    return true;
  }

  @Override
  @Test
  public void testCreateTableIncremental() throws Exception {
    getDestinationHandler().execute(getGenerator().createTable(getIncrementalDedupStream(), "", false));

    final Table table = bq.getTable(getNamespace(), "users_final");
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
            Field.newBuilder("_airbyte_generation_id", legacySQLTypeName(StandardSQLTypeName.INT64)).build(),
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
    final BigQueryDestinationHandler destinationHandler = new BigQueryDestinationHandler(bq, "asia-east1");
    // We're creating the dataset in the wrong location in the @BeforeEach block. Explicitly delete it.
    bq.getDataset(getNamespace()).delete();
    final var sqlGenerator = new BigQuerySqlGenerator(projectId, "asia-east1");
    destinationHandler.execute(sqlGenerator.createSchema(getNamespace()));
    destinationHandler.execute(sqlGenerator.createTable(getIncrementalDedupStream(), "", false));

    // Empirically, it sometimes takes Bigquery nearly 30 seconds to propagate the dataset's existence.
    // Give ourselves 2 minutes just in case.
    for (int i = 0; i < 120; i++) {
      final Dataset dataset = bq.getDataset(DatasetId.of(bq.getOptions().getProjectId(), getNamespace()));
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
   * Bigquery column names aren't allowed to start with certain prefixes. Verify that we throw an
   * error in these cases.
   */
  @ParameterizedTest
  @ValueSource(strings = {
    "_table_",
    "_file_",
    "_partition_",
    "_row_timestamp_",
    "__root__",
    "_colidentifier_"
  })
  public void testFailureOnReservedColumnNamePrefix(final String prefix) {
    final StreamConfig stream = new StreamConfig(
        getStreamId(),
        DestinationSyncMode.APPEND,
        Collections.emptyList(),
        Optional.empty(),
        new LinkedHashMap<>() {

          {
            put(getGenerator().buildColumnId(prefix + "the_column_name"), AirbyteProtocolType.STRING);
          }

        }, 0, 0, 0);

    final Sql createTable = getGenerator().createTable(stream, "", false);
    assertThrows(
        BigQueryException.class,
        () -> getDestinationHandler().execute(createTable));
  }

  /**
   * Something about this test is borked on bigquery. It fails because the raw table doesn't exist,
   * but you can go into the UI and see that it does exist.
   */
  @Override
  @Disabled
  public void noCrashOnSpecialCharacters(final String specialChars) throws Exception {
    super.noCrashOnSpecialCharacters(specialChars);
  }

  /**
   * Bigquery doesn't handle frequent INSERT/DELETE statements on a single table very well. So we
   * don't have real state handling. Disable this test.
   */
  @Override
  @Disabled
  @Test
  public void testStateHandling() throws Exception {
    super.testStateHandling();
  }

  /**
   * TableResult contains records in a somewhat nonintuitive format (and it avoids loading them all
   * into memory). That's annoying for us since we're working with small test data, so just pull
   * everything into a list.
   */
  public static List<JsonNode> toJsonRecords(final TableResult result) {
    return result.streamAll().map(row -> toJson(result.getSchema(), row)).toList();
  }

  /**
   * FieldValueList stores everything internally as string (I think?) but provides conversions to more
   * useful types. This method does that conversion, using the schema to determine which type is most
   * appropriate. Then we just dump everything into a jsonnode for interop with RecordDiffer.
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
          // naively converting an Instant returns a DecimalNode with the unix epoch, so instead we manually
          // stringify it
          case TIMESTAMP -> Jsons.jsonNode(value.getTimestampInstant().toString());
          // value.getTimestampInstant() fails to parse these types
          case DATE, DATETIME, TIME -> Jsons.jsonNode(value.getStringValue());
          // bigquery returns JSON columns as string; manually parse it into a JsonNode
          case JSON -> Jsons.jsonNode(Jsons.deserializeExact(value.getStringValue()));

          // Default case for weird types (struct, array, geography, interval, bytes)
          default -> Jsons.jsonNode(value.getStringValue());
        };
        json.set(field.getName(), typedValue);
      }
    }
    return json;
  }

  @Disabled
  public void testLongIdentifierHandling() {
    super.testLongIdentifierHandling();
  }

}
