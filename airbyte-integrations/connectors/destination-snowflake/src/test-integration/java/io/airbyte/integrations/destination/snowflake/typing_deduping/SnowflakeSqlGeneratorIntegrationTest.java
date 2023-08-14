package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toMap;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;

import autovalue.shaded.com.google.common.collect.ImmutableMap;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.destination.typing_deduping.BaseSqlGeneratorIntegrationTest;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.snowflake.OssCloudEnvVarConsts;
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabase;
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import javax.sql.DataSource;
import org.apache.commons.text.StringSubstitutor;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

@Disabled
public class SnowflakeSqlGeneratorIntegrationTest extends BaseSqlGeneratorIntegrationTest<SnowflakeTableDefinition> {

  private static String databaseName;
  private static JdbcDatabase database;
  private static DataSource dataSource;

  @BeforeAll
  public static void setupSnowflake() {
    JsonNode config = Jsons.deserialize(IOs.readFile(Path.of("secrets/1s1t_internal_staging_config.json")));
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
    return new SnowflakeSqlGenerator();
  }

  @Override
  protected SnowflakeDestinationHandler getDestinationHandler() {
    return new SnowflakeDestinationHandler(databaseName, database);
  }

  @Override
  protected void createNamespace(String namespace) throws SQLException {
    database.execute("CREATE SCHEMA \"" + namespace + '"');
  }

  @Override
  protected void createRawTable(StreamId streamId) throws Exception {
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
  protected void createFinalTable(boolean includeCdcDeletedAt, StreamId streamId, String suffix) throws Exception {
    String cdcDeletedAt = includeCdcDeletedAt ? "\"_ab_cdc_deleted_at\" TIMESTAMP_TZ," : "";
    database.execute(new StringSubstitutor(Map.of(
        "final_table_id", streamId.finalTableId(SnowflakeSqlGenerator.QUOTE, suffix),
        "cdc_deleted_at", cdcDeletedAt
    )).replace(
        """
            CREATE TABLE ${final_table_id} (
              "_airbyte_raw_id" TEXT NOT NULL,
              "_airbyte_extracted_at" TIMESTAMP_TZ NOT NULL,
              "_airbyte_meta" VARIANT NOT NULL,
              "id1" NUMBER,
              "id2" NUMBER,
              "updated_at" TIMESTAMP_TZ,
              ${cdc_deleted_at}
              "struct" OBJECT,
              "array" ARRAY,
              "string" TEXT,
              "number" FLOAT,
              "integer" NUMBER,
              "boolean" BOOLEAN,
              "timestamp_with_timezone" TIMESTAMP_TZ,
              "timestamp_without_timezone" TIMESTAMP_NTZ,
              "time_with_timezone" TEXT,
              "time_without_timezone" TIME,
              "date" DATE,
              "unknown" VARIANT
            )
            """));
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(StreamId streamId) throws Exception {
    return SnowflakeTestUtils.dumpRawTable(database, streamId.rawTableId(SnowflakeSqlGenerator.QUOTE));
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(StreamId streamId, String suffix) throws Exception {
    return SnowflakeTestUtils.dumpFinalTable(
        database,
        databaseName,
        namespace,
        streamId.finalName() + suffix);
  }

  @Override
  protected void teardownNamespace(String namespace) throws SQLException {
    database.execute("DROP SCHEMA IF EXISTS \"" + namespace + '"');
  }

  @Override
  protected void insertFinalTableRecords(boolean includeCdcDeletedAt, StreamId streamId, String suffix, List<JsonNode> records) throws Exception {
    List<String> columnNames = includeCdcDeletedAt ? FINAL_TABLE_COLUMN_NAMES_CDC : FINAL_TABLE_COLUMN_NAMES;
    String cdcDeletedAtName = includeCdcDeletedAt ? ",\"_ab_cdc_deleted_at\"" : "";
    String cdcDeletedAtExtract = includeCdcDeletedAt ? ",column19" : "";
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
                                                            return "$$" + stringContents + "$$";
                                                          })
                                                          .collect(joining(",")))
                                .map(row -> "(" + row + ")")
                                .collect(joining(","));

    database.execute(new StringSubstitutor(
        Map.of(
            "final_table_id", streamId.finalTableId(SnowflakeSqlGenerator.QUOTE, suffix),
            "cdc_deleted_at_name", cdcDeletedAtName,
            "cdc_deleted_at_extract", cdcDeletedAtExtract,
            "records", recordsText
        ),
        "#{",
        "}"
    ).replace(
        // Similar to insertRawTableRecords, some of these columns are declared as string and wrapped in parse_json().
        """
            INSERT INTO #{final_table_id} (
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
              "unknown"
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

  @Override
  protected void insertRawTableRecords(StreamId streamId, List<JsonNode> records) throws Exception {
    String recordsText = records.stream()
                                // For each record, convert it to a string like "(rawId, extractedAt, loadedAt, data)"
                                .map(record -> JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES.stream()
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
                                                                                            // Use dollar quotes to avoid needing to escape anything
                                                                                            return "$$" + stringContents + "$$";
                                                                                          })
                                                                                          .collect(joining(",")))
                                .map(row -> "(" + row + ")")
                                .collect(joining(","));
    database.execute(new StringSubstitutor(
        Map.of(
            "raw_table_id", streamId.rawTableId(SnowflakeSqlGenerator.QUOTE),
            "records_text", recordsText
        ),
        // Use different delimiters because we're using dollar quotes in the query.
        "#{",
        "}"
    ).replace(
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
            """
    ));
  }

  @Override
  @Test
  public void testCreateTableIncremental() throws Exception {
    String sql = generator.createTable(incrementalDedupStream, "");
    destinationHandler.execute(sql);

    Optional<String> tableKind = database.queryJsons(String.format("SHOW TABLES LIKE '%s' IN SCHEMA \"%s\";", "users_final", namespace))
                                         .stream().map(record -> record.get("kind").asText())
                                         .findFirst();
    Map<String, String> columns = database.queryJsons(
                                              """
                                                  SELECT column_name, data_type, numeric_precision, numeric_scale
                                                  FROM information_schema.columns
                                                  WHERE table_catalog = ?
                                                    AND table_schema = ?
                                                    AND table_name = ?
                                                  ORDER BY ordinal_position;
                                                  """,
                                              databaseName,
                                              namespace,
                                              "users_final"
                                          ).stream()
                                          .collect(toMap(
                                              record -> record.get("COLUMN_NAME").asText(),
                                              record -> {
                                                String type = record.get("DATA_TYPE").asText();
                                                if (type.equals("NUMBER")) {
                                                  return String.format("NUMBER(%s, %s)", record.get("NUMERIC_PRECISION").asText(),
                                                                       record.get("NUMERIC_SCALE").asText()
                                                  );
                                                }
                                                return type;
                                              }
                                          ));
    assertAll(
        () -> assertEquals(Optional.of("TABLE"), tableKind, "Table should be permanent, not transient"),
        () -> assertEquals(
            ImmutableMap.builder()
                        .put("_airbyte_raw_id", "TEXT")
                        .put("_airbyte_extracted_at", "TIMESTAMP_TZ")
                        .put("_airbyte_meta", "VARIANT")
                        .put("id1", "NUMBER(38, 0)")
                        .put("id2", "NUMBER(38, 0)")
                        .put("updated_at", "TIMESTAMP_TZ")
                        .put("struct", "OBJECT")
                        .put("array", "ARRAY")
                        .put("string", "TEXT")
                        .put("number", "FLOAT")
                        .put("integer", "NUMBER(38, 0)")
                        .put("boolean", "BOOLEAN")
                        .put("timestamp_with_timezone", "TIMESTAMP_TZ")
                        .put("timestamp_without_timezone", "TIMESTAMP_NTZ")
                        .put("time_with_timezone", "TEXT")
                        .put("time_without_timezone", "TIME")
                        .put("date", "DATE")
                        .put("unknown", "VARIANT")
                        .build(),
            columns
        )
    );
  }

  @Override
  protected void createV1RawTable(final StreamId v1RawTable) throws Exception {

  }

  @Override
  protected void insertV1RawTableRecords(final StreamId streamId, final List<JsonNode> records) throws Exception {

  }

  @Override
  public void testV1V2migration() throws Exception {
    super.testV1V2migration();
  }
}
