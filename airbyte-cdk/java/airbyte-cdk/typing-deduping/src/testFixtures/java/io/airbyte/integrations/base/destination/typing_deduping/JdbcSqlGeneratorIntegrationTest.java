/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.LEGACY_RAW_TABLE_COLUMNS;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import java.util.List;
import org.jooq.DSLContext;
import org.jooq.DataType;
import org.jooq.Name;
import org.jooq.SQLDialect;
import org.jooq.conf.ParamType;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;

public abstract class JdbcSqlGeneratorIntegrationTest<T> extends BaseSqlGeneratorIntegrationTest<T> {

  protected abstract JdbcDatabase getDatabase();

  protected abstract DataType<?> getStructType();

  protected abstract SQLDialect getSqlDialect();

  private DSLContext getDslContext() {
    return DSL.using(getSqlDialect());
  }

  protected abstract void insertRecords(final Name tableName,
                                        final List<String> columnNames,
                                        final List<JsonNode> records,
                                        final String... jsonColumns)
      throws Exception;

  @Override
  protected void createNamespace(String namespace) throws Exception {
    getDatabase().execute(getDslContext().createSchemaIfNotExists(namespace).getSQL(ParamType.INLINED));
  }

  @Override
  protected void createRawTable(StreamId streamId) throws Exception {
    getDatabase().execute(getDslContext().createTable(DSL.name(streamId.rawNamespace(), streamId.rawName()))
        .column(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36).nullable(false))
        .column(COLUMN_NAME_AB_EXTRACTED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false))
        .column(COLUMN_NAME_AB_LOADED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE)
        .column(COLUMN_NAME_DATA, getStructType().nullable(false))
        .getSQL(ParamType.INLINED));
  }

  @Override
  protected void createV1RawTable(StreamId v1RawTable) throws Exception {
    getDatabase().execute(getDslContext().createTable(DSL.name(v1RawTable.rawNamespace(), v1RawTable.rawName()))
        .column(COLUMN_NAME_AB_ID, SQLDataType.VARCHAR(36).nullable(false))
        .column(COLUMN_NAME_EMITTED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false))
        .column(COLUMN_NAME_DATA, getStructType().nullable(false))
        .getSQL(ParamType.INLINED));
  }

  @Override
  protected void insertRawTableRecords(StreamId streamId, List<JsonNode> records) throws Exception {
    insertRecords(
        DSL.name(streamId.rawNamespace(), streamId.rawName()),
        JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES,
        records,
        COLUMN_NAME_DATA);
  }

  @Override
  protected void insertV1RawTableRecords(StreamId streamId, List<JsonNode> records) throws Exception {
    insertRecords(
        DSL.name(streamId.rawNamespace(), streamId.rawName()),
        LEGACY_RAW_TABLE_COLUMNS,
        records,
        COLUMN_NAME_DATA);
  }

  @Override
  protected void insertFinalTableRecords(boolean includeCdcDeletedAt, StreamId streamId, String suffix, List<JsonNode> records) throws Exception {
    final List<String> columnNames = includeCdcDeletedAt ? FINAL_TABLE_COLUMN_NAMES_CDC : FINAL_TABLE_COLUMN_NAMES;
    insertRecords(
        DSL.name(streamId.finalNamespace(), streamId.finalName() + suffix),
        columnNames,
        records,
        COLUMN_NAME_AB_META, "struct", "array", "unknown");
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(StreamId streamId) throws Exception {
    return getDatabase().queryJsons(getDslContext().selectFrom(DSL.name(streamId.rawNamespace(), streamId.rawName())).getSQL(ParamType.INLINED));
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(StreamId streamId, String suffix) throws Exception {
    return getDatabase()
        .queryJsons(getDslContext().selectFrom(DSL.name(streamId.finalNamespace(), streamId.finalName() + suffix)).getSQL(ParamType.INLINED));
  }

  @Override
  protected void teardownNamespace(String namespace) throws Exception {
    getDatabase().execute(getDslContext().dropSchema(namespace).cascade().getSQL(ParamType.INLINED));
  }

}
