/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID;
import static org.jooq.impl.DSL.createSchemaIfNotExists;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.quotedName;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.CustomSqlType;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.SQLType;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.jooq.CreateSchemaFinalStep;
import org.jooq.CreateTableColumnStep;
import org.jooq.DSLContext;
import org.jooq.DataType;
import org.jooq.Field;
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
    List<Field<?>> fields =
        metaColumns.entrySet().stream().map(metaColumn -> field(quotedName(metaColumn.getKey()), metaColumn.getValue())).collect(Collectors.toList());
    List<Field<?>> dataFields =
        streamConfig.columns().entrySet().stream().map(column -> field(quotedName(column.getKey().name()), toDialectType(column.getValue()))).collect(
            Collectors.toList());
    fields.addAll(dataFields);
    return fields;
  }

  @Override
  public String createTable(final StreamConfig stream, final String suffix, final boolean force) {
    DSLContext dsl = getDslContext();
    CreateSchemaFinalStep createSchemaSql = createSchemaIfNotExists(quotedName(stream.id().finalNamespace()));

    // TODO: Use Naming transformer to sanitize these strings with redshift restrictions.
    String finalTableIdentifier = stream.id().finalName() + suffix.toLowerCase();
    Map<String, DataType<?>> metaColumns = new LinkedHashMap<>();
    metaColumns.put(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36).nullable(false));
    metaColumns.put(COLUMN_NAME_AB_EXTRACTED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    metaColumns.put(COLUMN_NAME_AB_META, getSuperType().nullable(false));
    CreateTableColumnStep createTableSql = dsl.createTable(quotedName(stream.id().finalNamespace(), finalTableIdentifier))
        .columns(buildFields(metaColumns, stream));
    return dsl.begin(createSchemaSql, createTableSql).getSQL();
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    return false;
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
    return null;
  }

  @Override
  public String migrateFromV1toV2(final StreamId streamId, final String namespace, final String tableName) {
    return null;
  }

  @Override
  public String clearLoadedAt(final StreamId streamId) {
    return null;
  }

}
