/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.*;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.BaseSqlGeneratorIntegrationTest;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.redshift.RedshiftInsertDestination;
import io.airbyte.integrations.destination.redshift.RedshiftSQLNameTransformer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.List;
import javax.sql.DataSource;
import org.jooq.InsertValuesStepN;
import org.jooq.Name;
import org.jooq.Record;
import org.jooq.impl.DSL;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

public class RedshiftSqlGeneratorIntegrationTest extends BaseSqlGeneratorIntegrationTest<TableDefinition> {

  private static DataSource dataSource;
  private static JdbcDatabase database;
  private static String databaseName = "integrationtests";

  @BeforeAll
  public static void setupJdbcDatasource() throws Exception {
    final String rawConfig = Files.readString(Path.of("secrets/1s1t_config.json"));
    final JsonNode config = Jsons.deserialize(rawConfig);
    // TODO: Existing in AbstractJdbcDestination, pull out to a util file
    databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    // TODO: Its sad to instantiate unneeded dependency to construct database and datsources. pull it to
    // static methods.
    final RedshiftInsertDestination insertDestination = new RedshiftInsertDestination();
    dataSource = insertDestination.getDataSource(config);
    database = insertDestination.getDatabase(dataSource);
  }

  @AfterAll
  public static void teardownSnowflake() throws Exception {
    DataSourceFactory.close(dataSource);
  }

  @Override
  protected SqlGenerator<TableDefinition> getSqlGenerator() {
    return new RedshiftSqlGenerator(new RedshiftSQLNameTransformer());
  }

  @Override
  protected DestinationHandler<TableDefinition> getDestinationHandler() {
    return new JdbcDestinationHandler(databaseName, database);
  }

  @Override
  protected void createNamespace(final String namespace) throws Exception {
    database.execute(DSL.createSchemaIfNotExists(namespace).getSQL());
  }

  @Override
  protected void createRawTable(final StreamId streamId) throws Exception {
    database.execute(DSL.createTable(DSL.name(streamId.rawNamespace(), streamId.rawName()))
        .column(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36).nullable(false))
        .column(COLUMN_NAME_AB_EXTRACTED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false))
        .column(COLUMN_NAME_AB_LOADED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE)
        .column(COLUMN_NAME_DATA, new DefaultDataType<>(null, String.class, "super").nullable(false))
        .getSQL());
  }

  @Override
  protected void createV1RawTable(final StreamId v1RawTable) throws Exception {
    database.execute(DSL.createTable(DSL.name(v1RawTable.rawNamespace(), v1RawTable.rawName()))
        .column(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36).nullable(false))
        .column(COLUMN_NAME_EMITTED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false))
        .column(COLUMN_NAME_DATA, new DefaultDataType<>(null, String.class, "super").nullable(false))
        .getSQL());
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(final StreamId streamId) throws Exception {
    return database.queryJsons(DSL.selectFrom(DSL.name(streamId.rawNamespace(), streamId.rawName())).getSQL());
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(final StreamId streamId, final String suffix) throws Exception {
    return database.queryJsons(DSL.selectFrom(DSL.name(streamId.finalNamespace(), streamId.finalName() + suffix)).getSQL());
  }

  @Override
  protected void teardownNamespace(final String namespace) throws Exception {
    database.execute(DSL.dropSchema(namespace).cascade().getSQL());
  }

  @Override
  protected void insertFinalTableRecords(final boolean includeCdcDeletedAt,
                                         final StreamId streamId,
                                         final String suffix,
                                         final List<JsonNode> records)
      throws Exception {
    final List<String> columnNames = includeCdcDeletedAt ? FINAL_TABLE_COLUMN_NAMES_CDC : FINAL_TABLE_COLUMN_NAMES;
    insertRecords(
        DSL.name(streamId.finalNamespace(), streamId.finalName() + suffix),
        columnNames,
        records,
        COLUMN_NAME_AB_META, "struct", "array", "unknown");
  }

  @Override
  protected void insertV1RawTableRecords(final StreamId streamId, final List<JsonNode> records) throws Exception {
    insertRecords(
        DSL.name(streamId.rawNamespace(), streamId.rawName()),
        LEGACY_RAW_TABLE_COLUMNS,
        records,
        COLUMN_NAME_DATA);
  }

  @Override
  protected void insertRawTableRecords(final StreamId streamId, final List<JsonNode> records) throws Exception {
    insertRecords(
        DSL.name(streamId.rawNamespace(), streamId.rawName()),
        JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES,
        records,
        COLUMN_NAME_DATA);
  }

  /**
   * Insert arbitrary records into an arbitrary table.
   *
   * @param columnsToParseJson Columns that must be wrapped in JSON_PARSE, because we're inserting them
   *                           into a SUPER column. Naively inserting a string results a SUPER value
   *                           containing a json string, rather than a json object.
   */
  private void insertRecords(final Name tableName, final List<String> columnNames, final List<JsonNode> records, final String... columnsToParseJson)
      throws SQLException {
    InsertValuesStepN<Record> insert = DSL.insertInto(
        DSL.table(tableName),
        columnNames.stream().map(DSL::field).toList());
    for (final JsonNode record : records) {
      insert = insert.values(
          columnNames.stream()
              .map(fieldName -> {
                // Convert this field to a string. Pretty naive implementation.
                final JsonNode column = record.get(fieldName);
                final String columnAsString;
                if (column == null) {
                  columnAsString = null;
                } else if (column.isTextual()) {
                  columnAsString = column.asText();
                } else {
                  columnAsString = column.toString();
                }

                if (Arrays.asList(columnsToParseJson).contains(fieldName)) {
                  // TODO this is redshift-specific. If we try and genericize this class, we need to handle this specifically
                  return DSL.function("JSON_PARSE", String.class, DSL.inline(columnAsString));
                } else {
                  return DSL.inline(columnAsString);
                }
              })
              .toList());
    }
    database.execute(insert.getSQL());
  }

  @Override
  @Test
  public void testCreateTableIncremental() throws Exception {
    // TODO
  }

}
