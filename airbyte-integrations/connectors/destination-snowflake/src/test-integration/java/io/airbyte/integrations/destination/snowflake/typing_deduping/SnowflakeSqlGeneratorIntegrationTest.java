/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeTypeAndDedupe;
import static io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.timestampToString;
import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toMap;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.BaseSqlGeneratorIntegrationTest;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.snowflake.OssCloudEnvVarConsts;
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabase;
import io.airbyte.integrations.destination.snowflake.SnowflakeSourceOperations;
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils;
import io.airbyte.integrations.destination.snowflake.migrations.SnowflakeState;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.sql.DataSource;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.text.StringSubstitutor;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public class SnowflakeSqlGeneratorIntegrationTest extends BaseSqlGeneratorIntegrationTest<SnowflakeState> {

  private static String databaseName;
  private static JdbcDatabase database;
  private static DataSource dataSource;

  @Override
  protected boolean getSupportsSafeCast() {
    return true;
  }

  @BeforeAll
  public static void setupSnowflake() {
    final JsonNode config = Jsons.deserialize(IOs.readFile(Path.of("secrets/1s1t_internal_staging_config.json")));
    databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    dataSource = SnowflakeDatabase.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS);
    database = SnowflakeDatabase.getDatabase(dataSource);
  }

  @AfterAll
  public static void teardownSnowflake() throws Exception {
    DataSourceFactory.close(dataSource);
  }

  @Override
  protected SnowflakeSqlGenerator getSqlGenerator() {
    return new SnowflakeSqlGenerator(0);
  }

  @Override
  protected SnowflakeDestinationHandler getDestinationHandler() {
    return new SnowflakeDestinationHandler(databaseName, database, getNamespace().toUpperCase());
  }

  @Override
  protected StreamId buildStreamId(final String namespace, final String finalTableName, final String rawTableName) {
    return new StreamId(namespace.toUpperCase(), finalTableName.toUpperCase(), namespace.toUpperCase(), rawTableName, namespace, finalTableName);
  }

  @Override
  protected void createNamespace(final String namespace) throws SQLException {
    database.execute("CREATE SCHEMA IF NOT EXISTS \"" + namespace.toUpperCase() + '"');
  }

  @Override
  protected void createRawTable(final StreamId streamId) throws Exception {
    database.execute(new StringSubstitutor(Map.of(
        "raw_table_id", streamId.rawTableId(SnowflakeSqlGenerator.QUOTE))).replace(
            """
            CREATE TABLE ${raw_table_id} (
              "_airbyte_raw_id" TEXT NOT NULL,
              "_airbyte_data" VARIANT NOT NULL,
              "_airbyte_extracted_at" TIMESTAMP_TZ NOT NULL,
              "_airbyte_loaded_at" TIMESTAMP_TZ
            )
            """));
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(final StreamId streamId) throws Exception {
    return SnowflakeTestUtils.dumpRawTable(database, streamId.rawTableId(SnowflakeSqlGenerator.QUOTE));
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(final StreamId streamId, final String suffix) throws Exception {
    return SnowflakeTestUtils.dumpFinalTable(
        database,
        databaseName,
        streamId.getFinalNamespace(),
        streamId.getFinalName() + suffix.toUpperCase());
  }

  @Override
  protected void teardownNamespace(final String namespace) throws SQLException {
    database.execute("DROP SCHEMA IF EXISTS \"" + namespace.toUpperCase() + '"');
  }

  @Override
  protected void insertFinalTableRecords(final boolean includeCdcDeletedAt,
                                         final StreamId streamId,
                                         final String suffix,
                                         final List<? extends JsonNode> records)
      throws Exception {
    final List<String> columnNames = includeCdcDeletedAt ? FINAL_TABLE_COLUMN_NAMES_CDC : FINAL_TABLE_COLUMN_NAMES;
    final String cdcDeletedAtName = includeCdcDeletedAt ? ",\"_AB_CDC_DELETED_AT\"" : "";
    final String cdcDeletedAtExtract = includeCdcDeletedAt ? ",column19" : "";
    final String recordsText = records.stream()
        // For each record, convert it to a string like "(rawId, extractedAt, loadedAt, data)"
        .map(record -> columnNames.stream()
            .map(record::get)
            .map(this::dollarQuoteWrap)
            .collect(joining(",")))
        .map(row -> "(" + row + ")")
        .collect(joining(","));

    database.execute(new StringSubstitutor(
        Map.of(
            "final_table_id", streamId.finalTableId(SnowflakeSqlGenerator.QUOTE, suffix.toUpperCase()),
            "cdc_deleted_at_name", cdcDeletedAtName,
            "cdc_deleted_at_extract", cdcDeletedAtExtract,
            "records", recordsText),
        "#{",
        "}").replace(
            // Similar to insertRawTableRecords, some of these columns are declared as string and wrapped in
            // parse_json().
            """
            INSERT INTO #{final_table_id} (
              "_AIRBYTE_RAW_ID",
              "_AIRBYTE_EXTRACTED_AT",
              "_AIRBYTE_META",
              "ID1",
              "ID2",
              "UPDATED_AT",
              "STRUCT",
              "ARRAY",
              "STRING",
              "NUMBER",
              "INTEGER",
              "BOOLEAN",
              "TIMESTAMP_WITH_TIMEZONE",
              "TIMESTAMP_WITHOUT_TIMEZONE",
              "TIME_WITH_TIMEZONE",
              "TIME_WITHOUT_TIMEZONE",
              "DATE",
              "UNKNOWN"
              #{cdc_deleted_at_name}
            )
            SELECT
              column1,
              column2,
              PARSE_JSON(column3),
              column4,
              column5,
              column6,
              PARSE_JSON(column7),
              PARSE_JSON(column8),
              column9,
              column10,
              column11,
              column12,
              column13,
              column14,
              column15,
              column16,
              column17,
              PARSE_JSON(column18)
              #{cdc_deleted_at_extract}
            FROM VALUES
              #{records}
            """));
  }

  private String dollarQuoteWrap(final JsonNode node) {
    if (node == null) {
      return "NULL";
    }
    final String stringContents = node.isTextual() ? node.asText() : node.toString();
    // Use dollar quotes to avoid needing to escape quotes
    return StringUtils.wrap(stringContents.replace("$$", "\\$\\$"), "$$");
  }

  @Override
  protected void insertRawTableRecords(final StreamId streamId, final List<? extends JsonNode> records) throws Exception {
    final String recordsText = records.stream()
        // For each record, convert it to a string like "(rawId, extractedAt, loadedAt, data)"
        .map(record -> JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES
            .stream()
            .map(record::get)
            .map(this::dollarQuoteWrap)
            .collect(joining(",")))
        .map(row -> "(" + row + ")")
        .collect(joining(","));
    database.execute(new StringSubstitutor(
        Map.of(
            "raw_table_id", streamId.rawTableId(SnowflakeSqlGenerator.QUOTE),
            "records_text", recordsText),
        // Use different delimiters because we're using dollar quotes in the query.
        "#{",
        "}").replace(
            // Snowflake doesn't let you directly insert a parse_json expression, so we have to use a subquery.
            """
            INSERT INTO #{raw_table_id} (
              "_airbyte_raw_id",
              "_airbyte_extracted_at",
              "_airbyte_loaded_at",
              "_airbyte_data"
            )
            SELECT
              column1,
              column2,
              column3,
              PARSE_JSON(column4)
            FROM VALUES
              #{records_text};
            """));
  }

  @Override
  protected Map<String, String> getFinalMetadataColumnNames() {
    return AbstractSnowflakeTypingDedupingTest.FINAL_METADATA_COLUMN_NAMES;
  }

  @Override
  @Test
  public void testCreateTableIncremental() throws Exception {
    final Sql sql = getGenerator().createTable(getIncrementalDedupStream(), "", false);
    getDestinationHandler().execute(sql);

    // Note that USERS_FINAL is uppercased here. This is intentional, because snowflake upcases unquoted
    // identifiers.
    final Optional<String> tableKind =
        database.queryJsons(String.format("SHOW TABLES LIKE '%s' IN SCHEMA \"%s\";", "USERS_FINAL", getNamespace().toUpperCase()))
            .stream().map(record -> record.get("kind").asText())
            .findFirst();
    final Map<String, String> columns = database.queryJsons(
        """
        SELECT column_name, data_type, numeric_precision, numeric_scale
        FROM information_schema.columns
        WHERE table_catalog = ?
          AND table_schema = ?
          AND table_name = ?
        ORDER BY ordinal_position;
        """,
        databaseName,
        getNamespace().toUpperCase(),
        "USERS_FINAL").stream()
        .collect(toMap(
            record -> record.get("COLUMN_NAME").asText(),
            record -> {
              final String type = record.get("DATA_TYPE").asText();
              if (type.equals("NUMBER")) {
                return String.format("NUMBER(%s, %s)", record.get("NUMERIC_PRECISION").asText(),
                    record.get("NUMERIC_SCALE").asText());
              }
              return type;
            }));
    assertAll(
        () -> assertEquals(Optional.of("TABLE"), tableKind, "Table should be permanent, not transient"),
        () -> assertEquals(
            ImmutableMap.builder()
                .put("_AIRBYTE_RAW_ID", "TEXT")
                .put("_AIRBYTE_EXTRACTED_AT", "TIMESTAMP_TZ")
                .put("_AIRBYTE_META", "VARIANT")
                .put("ID1", "NUMBER(38, 0)")
                .put("ID2", "NUMBER(38, 0)")
                .put("UPDATED_AT", "TIMESTAMP_TZ")
                .put("STRUCT", "OBJECT")
                .put("ARRAY", "ARRAY")
                .put("STRING", "TEXT")
                .put("NUMBER", "FLOAT")
                .put("INTEGER", "NUMBER(38, 0)")
                .put("BOOLEAN", "BOOLEAN")
                .put("TIMESTAMP_WITH_TIMEZONE", "TIMESTAMP_TZ")
                .put("TIMESTAMP_WITHOUT_TIMEZONE", "TIMESTAMP_NTZ")
                .put("TIME_WITH_TIMEZONE", "TEXT")
                .put("TIME_WITHOUT_TIMEZONE", "TIME")
                .put("DATE", "DATE")
                .put("UNKNOWN", "VARIANT")
                .build(),
            columns));
  }

  @Override
  protected void createV1RawTable(final StreamId v1RawTable) throws Exception {
    database.execute(String.format(
        """
            CREATE SCHEMA IF NOT EXISTS %s;
            CREATE TABLE IF NOT EXISTS %s.%s (
              %s VARCHAR PRIMARY KEY,
              %s VARIANT,
              %s TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp()
            ) data_retention_time_in_days = 0;
        """,
        v1RawTable.getRawNamespace(),
        v1RawTable.getRawNamespace(),
        v1RawTable.getRawName(),
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT));
  }

  @Override
  protected void insertV1RawTableRecords(final StreamId streamId, final List<? extends JsonNode> records) throws Exception {
    final var recordsText = records
        .stream()
        .map(record -> JavaBaseConstants.LEGACY_RAW_TABLE_COLUMNS
            .stream()
            .map(record::get)
            .map(value -> value == null ? "NULL" : value.isTextual() ? value.asText() : value.toString())
            .map(v -> "NULL".equals(v) ? v : StringUtils.wrap(v, "$$"))
            .collect(joining(",")))
        .map(row -> "(%s)".formatted(row))
        .collect(joining(","));
    final var insert = new StringSubstitutor(Map.of(
        "v1_raw_table_id", String.join(".", streamId.getRawNamespace(), streamId.getRawName()),
        "records", recordsText),
        // Use different delimiters because we're using dollar quotes in the query.
        "#{",
        "}").replace(
            """
            INSERT INTO #{v1_raw_table_id} (_airbyte_ab_id, _airbyte_data, _airbyte_emitted_at)
            SELECT column1, PARSE_JSON(column2), column3 FROM VALUES
              #{records};
            """);
    database.execute(insert);
  }

  @Override
  protected List<JsonNode> dumpV1RawTableRecords(final StreamId streamId) throws Exception {
    final var columns = Stream.of(
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        timestampToString(JavaBaseConstants.COLUMN_NAME_EMITTED_AT),
        JavaBaseConstants.COLUMN_NAME_DATA).collect(joining(","));
    return database.bufferedResultSetQuery(connection -> connection.createStatement().executeQuery(new StringSubstitutor(Map.of(
        "columns", columns,
        "table", String.join(".", streamId.getRawNamespace(), streamId.getRawName()))).replace(
            """
            SELECT ${columns} FROM ${table} ORDER BY _airbyte_emitted_at ASC
            """)),
        new SnowflakeSourceOperations()::rowToJson);
  }

  @Override
  protected void migrationAssertions(final List<? extends JsonNode> v1RawRecords, final List<? extends JsonNode> v2RawRecords) {
    final var v2RecordMap = v2RawRecords.stream().collect(Collectors.toMap(
        record -> record.get(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID).asText(),
        Function.identity()));
    assertAll(
        () -> assertEquals(5, v1RawRecords.size()),
        () -> assertEquals(5, v2RawRecords.size()));
    v1RawRecords.forEach(v1Record -> {
      final var v1id = v1Record.get(JavaBaseConstants.COLUMN_NAME_AB_ID.toUpperCase()).asText();
      assertAll(
          () -> assertEquals(v1id, v2RecordMap.get(v1id).get(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID).asText()),
          () -> assertEquals(v1Record.get(JavaBaseConstants.COLUMN_NAME_EMITTED_AT.toUpperCase()).asText(),
              v2RecordMap.get(v1id).get(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT).asText()),
          () -> assertNull(v2RecordMap.get(v1id).get(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT)));
      JsonNode originalData = v1Record.get(JavaBaseConstants.COLUMN_NAME_DATA.toUpperCase());
      JsonNode migratedData = v2RecordMap.get(v1id).get(JavaBaseConstants.COLUMN_NAME_DATA);
      migratedData = migratedData.isTextual() ? Jsons.deserializeExact(migratedData.asText()) : migratedData;
      originalData = originalData.isTextual() ? Jsons.deserializeExact(migratedData.asText()) : originalData;
      // hacky thing because we only care about the data contents.
      // diffRawTableRecords makes some assumptions about the structure of the blob.
      getDIFFER().diffFinalTableRecords(List.of(originalData), List.of(migratedData));
    });
  }

  @Disabled("We removed the optimization to only set the loaded_at column for new records after certain _extracted_at")
  @Test
  @Override
  public void ignoreOldRawRecords() throws Exception {
    super.ignoreOldRawRecords();
  }

  /**
   * Verify that the final table does not include NON-NULL PKs (after
   * https://github.com/airbytehq/airbyte/pull/31082)
   */
  @Test
  public void ensurePKsAreIndexedUnique() throws Exception {
    createRawTable(getStreamId());
    insertRawTableRecords(
        getStreamId(),
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

    final Sql createTable = getGenerator().createTable(getIncrementalDedupStream(), "", false);

    // should be OK with new tables
    getDestinationHandler().execute(createTable);
    List<DestinationInitialStatus<SnowflakeState>> initialStates = getDestinationHandler().gatherInitialState(List.of(getIncrementalDedupStream()));
    assertEquals(1, initialStates.size());
    assertFalse(initialStates.getFirst().isSchemaMismatch());
    getDestinationHandler().execute(Sql.of("DROP TABLE " + getStreamId().finalTableId("")));

    // Hack the create query to add NOT NULLs to emulate the old behavior
    List<List<String>> createTableModified = createTable.transactions().stream().map(transaction -> transaction.stream()
        .map(statement -> Arrays.stream(statement.split(System.lineSeparator())).map(
            line -> !line.contains("CLUSTER") && (line.contains("id1") || line.contains("id2") || line.contains("ID1") || line.contains("ID2"))
                ? line.replace(",", " NOT NULL,")
                : line)
            .collect(joining("\r\n")))
        .toList()).toList();
    getDestinationHandler().execute(new Sql(createTableModified));
    initialStates = getDestinationHandler().gatherInitialState(List.of(getIncrementalDedupStream()));
    assertEquals(1, initialStates.size());
    assertTrue(initialStates.get(0).isSchemaMismatch());
  }

  @Test
  public void dst_test_oldSyncRunsThroughTransition_thenNewSyncRuns_dedup() throws Exception {
    this.createRawTable(this.getStreamId());
    this.createFinalTable(this.getIncrementalDedupStream(), "");
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // 2 records written by a sync running on the old version of snowflake
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst local tz 1",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00-08:00",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice00"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst local tz 2",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00-07:00",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob00"
                            }
                          }
                          """),
        // and 2 records that got successfully loaded.
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst local tz 3",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00-08:00",
                            "_airbyte_loaded_at": "1970-01-01T00:00:00Z",
                            "_airbyte_data": {
                              "id1": 3,
                              "id2": 100,
                              "string": "Charlie00"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst local tz 4",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00-07:00",
                            "_airbyte_loaded_at": "1970-01-01T00:00:00Z",
                            "_airbyte_data": {
                              "id1": 4,
                              "id2": 100,
                              "string": "Dave00"
                            }
                          }
                          """)));
    this.insertFinalTableRecords(false, this.getStreamId(), "", List.of(
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst local tz 3",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00-08:00",
                            "_airbyte_meta": {"errors": []},
                            "id1": 3,
                            "id2": 100,
                            "string": "Charlie00"
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst local tz 4",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00-07:00",
                            "_airbyte_meta": {"errors": []},
                            "id1": 4,
                            "id2": 100,
                            "string": "Dave00"
                          }
                          """)));
    // Gather initial state at the start of our updated sync
    DestinationInitialStatus<SnowflakeState> initialState =
        this.getDestinationHandler().gatherInitialState(List.of(this.getIncrementalDedupStream())).getFirst();
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // insert raw records with updates
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice01"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 2",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob01"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 3",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 3,
                              "id2": 100,
                              "string": "Charlie01"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 4",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 4,
                              "id2": 100,
                              "string": "Dave01"
                            }
                          }
                          """)));

    executeTypeAndDedupe(this.getGenerator(), this.getDestinationHandler(), this.getIncrementalDedupStream(),
        initialState.initialRawTableStatus().getMaxProcessedTimestamp(), "");

    getDIFFER().diffFinalTableRecords(
        List.of(
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice01"
                              }
                              """),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob01"
                              }
                              """),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 3",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 3,
                                "ID2": 100,
                                "STRING": "Charlie01"
                              }
                              """),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 4",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 4,
                                "ID2": 100,
                                "STRING": "Dave01"
                              }
                              """)),
        this.dumpFinalTableRecords(this.getStreamId(), ""));
  }

  @Test
  public void dst_test_oldSyncRunsBeforeTransition_thenNewSyncRunsThroughTransition_dedup() throws Exception {
    this.createRawTable(this.getStreamId());
    this.createFinalTable(this.getIncrementalDedupStream(), "");
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // record written by a sync running on the old version of snowflake
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst local tz 1",
                            "_airbyte_extracted_at": "2024-03-10T01:59:00-08:00",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice00"
                            }
                          }
                          """)));
    // Gather initial state at the start of our updated sync
    DestinationInitialStatus<SnowflakeState> initialState =
        this.getDestinationHandler().gatherInitialState(List.of(this.getIncrementalDedupStream())).getFirst();
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // update the record twice
        // this never really happens, but verify that it works
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice01"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice02"
                            }
                          }
                          """)));

    executeTypeAndDedupe(this.getGenerator(), this.getDestinationHandler(), this.getIncrementalDedupStream(),
        initialState.initialRawTableStatus().getMaxProcessedTimestamp(), "");

    getDIFFER().diffFinalTableRecords(
        List.of(
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice02"
                              }
                              """)),
        this.dumpFinalTableRecords(this.getStreamId(), ""));
  }

  @Test
  public void dst_test_oldSyncRunsBeforeTransition_thenNewSyncRunsBeforeTransition_thenNewSyncRunsThroughTransition_dedup() throws Exception {
    this.createRawTable(this.getStreamId());
    this.createFinalTable(this.getIncrementalDedupStream(), "");
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // records written by a sync running on the old version of snowflake
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst local tz 1",
                            "_airbyte_extracted_at": "2024-03-10T01:59:00-08:00",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice00"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst local tz 2",
                            "_airbyte_extracted_at": "2024-03-10T01:59:00-08:00",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob00"
                            }
                          }
                          """)));

    // Gather initial state at the start of our first new sync
    DestinationInitialStatus<SnowflakeState> initialState =
        this.getDestinationHandler().gatherInitialState(List.of(this.getIncrementalDedupStream())).getFirst();
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // update the records
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice01"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst utc 2",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00Z",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob01"
                            }
                          }
                          """)));

    executeTypeAndDedupe(this.getGenerator(), this.getDestinationHandler(), this.getIncrementalDedupStream(),
        initialState.initialRawTableStatus().getMaxProcessedTimestamp(), "");

    getDIFFER().diffFinalTableRecords(
        List.of(
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice01"
                              }
                              """),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob01"
                              }
                              """)),
        this.dumpFinalTableRecords(this.getStreamId(), ""));

    // Gather initial state at the start of our second new sync
    DestinationInitialStatus<SnowflakeState> initialState2 =
        this.getDestinationHandler().gatherInitialState(List.of(this.getIncrementalDedupStream())).getFirst();
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // update the records again
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice02"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 2",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00Z",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob02"
                            }
                          }
                          """)));

    executeTypeAndDedupe(this.getGenerator(), this.getDestinationHandler(), this.getIncrementalDedupStream(),
        initialState2.initialRawTableStatus().getMaxProcessedTimestamp(), "");

    getDIFFER().diffFinalTableRecords(
        List.of(
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice02"
                              }
                              """),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob02"
                              }
                              """)),
        this.dumpFinalTableRecords(this.getStreamId(), ""));
  }

  @Test
  public void dst_test_oldSyncRunsThroughTransition_thenNewSyncRuns_append() throws Exception {
    this.createRawTable(this.getStreamId());
    this.createFinalTable(this.getIncrementalAppendStream(), "");
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // 2 records written by a sync running on the old version of snowflake
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst local tz 1",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00-08:00",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice00"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst local tz 2",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00-07:00",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob00"
                            }
                          }
                          """),
        // and 2 records that got successfully loaded with local TZ.
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst local tz 3",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00-08:00",
                            "_airbyte_loaded_at": "1970-01-01T00:00:00Z",
                            "_airbyte_data": {
                              "id1": 3,
                              "id2": 100,
                              "string": "Charlie00"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst local tz 4",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00-07:00",
                            "_airbyte_loaded_at": "1970-01-01T00:00:00Z",
                            "_airbyte_data": {
                              "id1": 4,
                              "id2": 100,
                              "string": "Dave00"
                            }
                          }
                          """)));
    this.insertFinalTableRecords(false, this.getStreamId(), "", List.of(
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst local tz 3",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00-08:00",
                            "_airbyte_meta": {"errors": []},
                            "id1": 3,
                            "id2": 100,
                            "string": "Charlie00"
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst local tz 4",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00-07:00",
                            "_airbyte_meta": {"errors": []},
                            "id1": 4,
                            "id2": 100,
                            "string": "Dave00"
                          }
                          """)));
    // Gather initial state at the start of our updated sync
    DestinationInitialStatus<SnowflakeState> initialState =
        this.getDestinationHandler().gatherInitialState(List.of(this.getIncrementalAppendStream())).getFirst();
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // insert raw records with updates
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice01"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 2",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob01"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 3",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 3,
                              "id2": 100,
                              "string": "Charlie01"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 4",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 4,
                              "id2": 100,
                              "string": "Dave01"
                            }
                          }
                          """)));

    executeTypeAndDedupe(this.getGenerator(), this.getDestinationHandler(), this.getIncrementalAppendStream(),
        initialState.initialRawTableStatus().getMaxProcessedTimestamp(), "");

    getDIFFER().diffFinalTableRecords(
        List.of(
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice00"
                              }
                              """),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice01"
                              }
                              """),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst local tz 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob00"
                              }"""),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob01"
                              }
                              """),
            // note local TZ here. This record was loaded by an older version of the connector.
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 3",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000-08:00",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 3,
                                "ID2": 100,
                                "STRING": "Charlie00"
                              }"""),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 3",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 3,
                                "ID2": 100,
                                "STRING": "Charlie01"
                              }
                              """),
            // note local TZ here. This record was loaded by an older version of the connector.
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst local tz 4",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000-07:00",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 4,
                                "ID2": 100,
                                "STRING": "Dave00"
                              }"""),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 4",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 4,
                                "ID2": 100,
                                "STRING": "Dave01"
                              }
                              """)),
        this.dumpFinalTableRecords(this.getStreamId(), ""));
  }

  @Test
  public void dst_test_oldSyncRunsBeforeTransition_thenNewSyncRunsThroughTransition_append() throws Exception {
    this.createRawTable(this.getStreamId());
    this.createFinalTable(this.getIncrementalAppendStream(), "");
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // record written by a sync running on the old version of snowflake
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst local tz 1",
                            "_airbyte_extracted_at": "2024-03-10T01:59:00-08:00",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice00"
                            }
                          }
                          """)));
    // Gather initial state at the start of our updated sync
    DestinationInitialStatus<SnowflakeState> initialState =
        this.getDestinationHandler().gatherInitialState(List.of(this.getIncrementalAppendStream())).getFirst();
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // update the record twice
        // this never really happens, but verify that it works
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice01"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice02"
                            }
                          }
                          """)));

    executeTypeAndDedupe(this.getGenerator(), this.getDestinationHandler(), this.getIncrementalAppendStream(),
        initialState.initialRawTableStatus().getMaxProcessedTimestamp(), "");

    getDIFFER().diffFinalTableRecords(
        List.of(
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T01:59:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice00"
                              }"""),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice01"
                              }"""),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice02"
                              }
                              """)),
        this.dumpFinalTableRecords(this.getStreamId(), ""));
  }

  @Test
  public void dst_test_oldSyncRunsBeforeTransition_thenNewSyncRunsBeforeTransition_thenNewSyncRunsThroughTransition_append() throws Exception {
    this.createRawTable(this.getStreamId());
    this.createFinalTable(this.getIncrementalAppendStream(), "");
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // records written by a sync running on the old version of snowflake
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst local tz 1",
                            "_airbyte_extracted_at": "2024-03-10T01:59:00-08:00",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice00"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst local tz 2",
                            "_airbyte_extracted_at": "2024-03-10T01:59:00-08:00",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob00"
                            }
                          }
                          """)));

    // Gather initial state at the start of our first new sync
    DestinationInitialStatus<SnowflakeState> initialState =
        this.getDestinationHandler().gatherInitialState(List.of(this.getIncrementalAppendStream())).getFirst();
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // update the records
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice01"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "pre-dst utc 2",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00Z",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob01"
                            }
                          }
                          """)));

    executeTypeAndDedupe(this.getGenerator(), this.getDestinationHandler(), this.getIncrementalAppendStream(),
        initialState.initialRawTableStatus().getMaxProcessedTimestamp(), "");

    getDIFFER().diffFinalTableRecords(
        List.of(
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T01:59:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice00"
                              }"""),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice01"
                              }
                              """),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T01:59:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob00"
                              }"""),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob01"
                              }
                              """)),
        this.dumpFinalTableRecords(this.getStreamId(), ""));

    // Gather initial state at the start of our second new sync
    DestinationInitialStatus<SnowflakeState> initialState2 =
        this.getDestinationHandler().gatherInitialState(List.of(this.getIncrementalAppendStream())).getFirst();
    this.insertRawTableRecords(this.getStreamId(), List.of(
        // update the records again
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice02"
                            }
                          }
                          """),
        Jsons.deserialize("""
                          {
                            "_airbyte_raw_id": "post-dst utc 2",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00Z",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob02"
                            }
                          }
                          """)));

    executeTypeAndDedupe(this.getGenerator(), this.getDestinationHandler(), this.getIncrementalAppendStream(),
        initialState2.initialRawTableStatus().getMaxProcessedTimestamp(), "");

    getDIFFER().diffFinalTableRecords(
        List.of(
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T01:59:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice00"
                              }"""),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice01"
                              }"""),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice02"
                              }
                              """),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T01:59:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob00"
                              }"""),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob01"
                              }"""),
            Jsons.deserialize("""
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob02"
                              }
                              """)),
        this.dumpFinalTableRecords(this.getStreamId(), ""));
  }

  // This is disabled because snowflake doesn't transform long identifiers
  @Disabled
  public void testLongIdentifierHandling() {
    super.testLongIdentifierHandling();
  }

}
