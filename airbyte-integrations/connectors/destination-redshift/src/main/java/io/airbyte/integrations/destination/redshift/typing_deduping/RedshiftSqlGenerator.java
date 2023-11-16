/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT;
import static java.util.Collections.emptySet;
import static java.util.stream.Collectors.toSet;
import static org.jooq.impl.DSL.createSchemaIfNotExists;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.quotedName;

import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.CustomSqlType;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.SQLType;
import java.time.Instant;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.jooq.CreateSchemaFinalStep;
import org.jooq.CreateTableColumnStep;
import org.jooq.DSLContext;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.Name;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;

public class RedshiftSqlGenerator extends JdbcSqlGenerator {

  public RedshiftSqlGenerator(final NamingConventionTransformer namingTransformer) {
    super(namingTransformer);
  }

  @Override
  protected String vendorId() {
    return "REDSHIFT";
  }

  @Override
  protected SQLType widestType() {
    // Vendor specific stuff I don't think matters for us since we're just pulling out the name
    return new CustomSqlType("SUPER", vendorId(), 123);
  }

  /**
   * This method returns Jooq internal DataType, Ideally we need to implement DataType interface with
   * all the required fields for Jooq typed query construction
   *
   * @return
   */
  private DataType<?> getSuperType() {
    return new DefaultDataType<>(null, String.class, "super");
  }

  @Override
  protected DataType<?> getStructType() {
    return getSuperType();
  }

  @Override
  protected DataType<?> getArrayType() {
    return getSuperType();
  }

  @Override
  protected DataType<?> getWidestType() {
    return getSuperType();
  }

  // TODO: Pull it into base class as abstract and formatted only for testing.
  protected DSLContext getDslContext() {
    // return DSL.using(SQLDialect.POSTGRES, new Settings().withRenderFormatted(true));
    return DSL.using(SQLDialect.POSTGRES);
  }

  /**
   * Notes about Redshift specific SQL * 16MB Limit on the total size of the SQL sent in a session *
   * Default mode of casting within SUPER is lax mode, to enable strict use SET
   * cast_super_null_on_error='OFF'; * *
   * https://docs.aws.amazon.com/redshift/latest/dg/super-configurations.html *
   * https://docs.aws.amazon.com/redshift/latest/dg/r_MERGE.html#r_MERGE_usage_notes * * (Cannot use
   * WITH clause in MERGE statement).
   * https://cloud.google.com/bigquery/docs/migration/redshift-sql#merge_statement * *
   * https://docs.aws.amazon.com/redshift/latest/dg/r_WITH_clause.html#r_WITH_clause-usage-notes *
   * Primary keys are informational only and not enforced
   * (https://docs.aws.amazon.com/redshift/latest/dg/t_Defining_constraints.html)
   */

  List<Field<?>> buildFields(final Map<String, DataType<?>> metaColumns, final StreamConfig streamConfig) {
    final List<Field<?>> fields =
        metaColumns.entrySet().stream().map(metaColumn -> field(quotedName(metaColumn.getKey()), metaColumn.getValue())).collect(Collectors.toList());
    final List<Field<?>> dataFields =
        streamConfig.columns().entrySet().stream().map(column -> field(quotedName(column.getKey().name()), toDialectType(column.getValue()))).collect(
            Collectors.toList());
    fields.addAll(dataFields);
    return fields;
  }

  @Override
  public String createTable(final StreamConfig stream, final String suffix, final boolean force) {
    final DSLContext dsl = getDslContext();
    final CreateSchemaFinalStep createSchemaSql = createSchemaIfNotExists(quotedName(stream.id().finalNamespace()));

    // TODO: Use Naming transformer to sanitize these strings with redshift restrictions.
    final String finalTableIdentifier = stream.id().finalName() + suffix.toLowerCase();
    final Map<String, DataType<?>> metaColumns = new LinkedHashMap<>();
    metaColumns.put(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36).nullable(false));
    metaColumns.put(COLUMN_NAME_AB_EXTRACTED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    metaColumns.put(COLUMN_NAME_AB_META, getSuperType().nullable(false));
    final CreateTableColumnStep createTableSql = dsl.createTable(quotedName(stream.id().finalNamespace(), finalTableIdentifier))
        .columns(buildFields(metaColumns, stream));
    return createSchemaSql.getSQL() + ";" + System.lineSeparator() + createTableSql.getSQL() + ";";
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    // Check that the columns match, with special handling for the metadata columns.
    final LinkedHashMap<Object, Object> intendedColumns = stream.columns().entrySet().stream()
        .collect(LinkedHashMap::new,
            (map, column) -> map.put(column.getKey().name(), toDialectType(column.getValue())),
            LinkedHashMap::putAll);
    final LinkedHashMap<String, String> actualColumns = existingTable.columns().entrySet().stream()
        .filter(column -> JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS.stream().map(String::toUpperCase)
            .noneMatch(airbyteColumnName -> airbyteColumnName.equals(column.getKey())))
        .collect(LinkedHashMap::new,
            (map, column) -> map.put(column.getKey(), column.getValue().type()),
            LinkedHashMap::putAll);

    final boolean sameColumns = actualColumns.equals(intendedColumns)
        && "varchar".equals(existingTable.columns().get(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID.toUpperCase()).type())
        && "timestamptz".equals(existingTable.columns().get(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT.toUpperCase()).type())
        && "super".equals(existingTable.columns().get(JavaBaseConstants.COLUMN_NAME_AB_META.toUpperCase()).type());

    return sameColumns;
  }

  @Override
  public String updateTable(final StreamConfig stream,
                            final String finalSuffix,
                            final Optional<Instant> minRawTimestamp,
                            final boolean useExpensiveSaferCasting) {
    return null;
  }

  @Override
  public String overwriteFinalTable(final StreamId stream, final String finalSuffix) {
    return DSL.alterTable(DSL.name(stream.finalNamespace(), stream.finalName() + finalSuffix))
        .renameTo(DSL.name(stream.finalName()))
        .getSQL();
  }

  @Override
  public String migrateFromV1toV2(final StreamId streamId, final String namespace, final String tableName) {
    final Name rawTableName = DSL.name(streamId.rawNamespace(), streamId.rawName());
    return Strings.join(
        List.of(
            DSL.createSchemaIfNotExists(streamId.rawNamespace()).getSQL(),
            DSL.dropTableIfExists(rawTableName).getSQL(),
            DSL.createTable(rawTableName)
                .column(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36).nullable(false))
                .column(COLUMN_NAME_AB_EXTRACTED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false))
                .column(COLUMN_NAME_AB_LOADED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false))
                .column(COLUMN_NAME_DATA, getSuperType().nullable(false))
                .as(DSL.select(
                    DSL.field(COLUMN_NAME_AB_ID).as(COLUMN_NAME_AB_RAW_ID),
                    DSL.field(COLUMN_NAME_EMITTED_AT).as(COLUMN_NAME_AB_EXTRACTED_AT),
                    DSL.inline(null, SQLDataType.TIMESTAMPWITHTIMEZONE).as(COLUMN_NAME_AB_LOADED_AT),
                    DSL.field(COLUMN_NAME_DATA).as(COLUMN_NAME_DATA)).from(DSL.table(DSL.name(namespace, tableName))))
                .getSQL()),
        ";\n");
  }

  @Override
  public String clearLoadedAt(final StreamId streamId) {
    return DSL.update(DSL.table(DSL.name(streamId.rawNamespace(), streamId.rawName())))
        .set(DSL.field(COLUMN_NAME_AB_LOADED_AT), (Object) null)
        .getSQL();
  }

}
