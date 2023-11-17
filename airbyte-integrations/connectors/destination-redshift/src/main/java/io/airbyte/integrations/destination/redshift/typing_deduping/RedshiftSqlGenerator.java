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
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.cast;
import static org.jooq.impl.DSL.createSchemaIfNotExists;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.function;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.rowNumber;
import static org.jooq.impl.DSL.select;
import static org.jooq.impl.DSL.table;
import static org.jooq.impl.DSL.val;
import static org.jooq.impl.DSL.with;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.CustomSqlType;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import java.sql.SQLType;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.jooq.CommonTableExpression;
import org.jooq.Condition;
import org.jooq.CreateSchemaFinalStep;
import org.jooq.CreateTableColumnStep;
import org.jooq.DSLContext;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.InsertValuesStepN;
import org.jooq.Name;
import org.jooq.Record;
import org.jooq.SQLDialect;
import org.jooq.SelectConditionStep;
import org.jooq.conf.ParamType;
import org.jooq.conf.Settings;
import org.jooq.impl.DSL;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;

public class RedshiftSqlGenerator extends JdbcSqlGenerator {

  private static final Map<String, String> REDSHIFT_TYPE_NAME_TO_JDBC_TYPE = ImmutableMap.of(
      "float8", "float",
      "int8", "bigint",
      "bool", "boolean",
      "timestamptz", "timestamp with time zone",
      "timetz", "time with time zone");
  private static final String COLUMN_ERROR_MESSAGE_FORMAT = "Problem with `%s`";
  private static final String AIRBYTE_META_COLUMN_ERRORS_KEY = "errors";

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
    return DSL.using(SQLDialect.POSTGRES, new Settings().withRenderFormatted(true));
    // return DSL.using(SQLDialect.POSTGRES);
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
   * (https://docs.aws.amazon.com/redshift/latest/dg/t_Defining_constraints.html) TODO: Look at SORT
   * KEYS, DISTKEY in redshift for optimizing the query performance.
   */

  /**
   * build jooq fields for final table with customers columns first and then meta columns.
   *
   * @param columns
   * @param metaColumns
   * @return
   */
  @VisibleForTesting
  List<Field<?>> buildFinalTableFields(final LinkedHashMap<ColumnId, AirbyteType> columns, final Map<String, DataType<?>> metaColumns) {
    final List<Field<?>> fields =
        metaColumns.entrySet().stream().map(metaColumn -> field(quotedName(metaColumn.getKey()), metaColumn.getValue())).collect(Collectors.toList());
    final List<Field<?>> dataFields =
        columns.entrySet().stream().map(column -> field(quotedName(column.getKey().name()), toDialectType(column.getValue()))).collect(
            Collectors.toList());
    dataFields.addAll(fields);
    return dataFields;
  }

  /**
   * build jooq fields for raw table with type-casted data columns first and then meta columns without
   * _airbyte_meta.
   *
   * @param columns
   * @param metaColumns
   * @return
   */
  @VisibleForTesting
  List<Field<?>> buildRawTableSelectFields(final LinkedHashMap<ColumnId, AirbyteType> columns, final Map<String, DataType<?>> metaColumns) {
    final List<Field<?>> fields =
        metaColumns.entrySet().stream().map(metaColumn -> field(quotedName(metaColumn.getKey()), metaColumn.getValue())).collect(Collectors.toList());
    final List<Field<?>> dataFields = columns
        .entrySet()
        .stream()
        .map(column -> cast(field(quotedName(COLUMN_NAME_DATA, column.getKey().name())), toDialectType(column.getValue())))
        .collect(Collectors.toList());
    dataFields.addAll(fields);
    return dataFields;
  }

  Field<?> arrayConcatStmt(List<Field<?>> arrays) {
    if (arrays.isEmpty()) {
      return field(""); // Return an empty string if the list is empty
    }

    // Base case: if there's only one element, return it
    if (arrays.size() == 1) {
      return arrays.get(0);
    }

    // Recursive case: construct ARRAY_CONCAT function call
    Field<?> lastValue = arrays.get(arrays.size() - 1);
    Field<?> recursiveCall = arrayConcatStmt(arrays.subList(0, arrays.size() - 1));

    return function("ARRAY_CONCAT", getSuperType(), recursiveCall, lastValue);
  }

  Field<?> toCastingErrorCaseStmt(final ColumnId column, final AirbyteType type) {
    final String caseStatementSqlTemplate = "CASE WHEN {0} THEN {1} ELSE {2} END ";
    final Field<?> field = field(quotedName(COLUMN_NAME_DATA, column.name()));
    final Condition typeCheckCondition = typeCheckCondition(field, type);
    return field(caseStatementSqlTemplate,
                 field.isNotNull().and(typeCheckCondition).and(cast(field, toDialectType(type)).isNull())
                 , function("ARRAY", getSuperType(), val(COLUMN_ERROR_MESSAGE_FORMAT.formatted(column.name()))), field("ARRAY()")
    );
  }

  // Sadly can't reuse the toDialectType because it returns Generics of DataType<?>
  Condition typeCheckCondition(final Field<?> field, final AirbyteType type) {
    if (type instanceof final AirbyteProtocolType airbyteProtocolType) {
      return typeCheckCondition(field, airbyteProtocolType);
    }
    return switch (type.getTypeName()) {
      case Struct.TYPE, UnsupportedOneOf.TYPE -> function("JSON_TYPEOF", SQLDataType.VARCHAR, field).eq("object");
      case Array.TYPE -> function("JSON_TYPEOF", SQLDataType.VARCHAR, field).eq("array");
      // No nested Unions supported so this will definitely not result in infinite recursion.
      case Union.TYPE -> typeCheckCondition(field, ((Union) type).chooseType());
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
    };
  }

  Condition typeCheckCondition(final Field<?> field, final AirbyteProtocolType airbyteProtocolType) {
    Condition defaultCondition = function("JSON_TYPEOF", SQLDataType.VARCHAR, field).eq("string");
    return switch (airbyteProtocolType) {
      case STRING -> function("IS_VARCHAR", SQLDataType.BOOLEAN, field).eq(true);
      case NUMBER -> function("IS_FLOAT", SQLDataType.BOOLEAN, field).eq(true);
      case INTEGER -> function("IS_BIGINT", SQLDataType.BOOLEAN, field).eq(true);
      case BOOLEAN -> function("IS_BOOLEAN", SQLDataType.BOOLEAN, field).eq(true);
      // Time data types are just string in redshift SUPER.
      case TIMESTAMP_WITH_TIMEZONE, TIMESTAMP_WITHOUT_TIMEZONE, TIME_WITHOUT_TIMEZONE, TIME_WITH_TIMEZONE, DATE, UNKNOWN -> defaultCondition;
    };
  }

  Field<?> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> columns) {
    final List<Field<?>> dataFields = columns
        .entrySet()
        .stream()
        .map(column -> toCastingErrorCaseStmt(column.getKey(), column.getValue()))
        .collect(Collectors.toList());
    return function("object", getSuperType(), val(AIRBYTE_META_COLUMN_ERRORS_KEY), arrayConcatStmt(dataFields)).as(COLUMN_NAME_AB_META);

  }

  /**
   * Use this method to get the final table meta columns with or without _airbyte_meta column.
   *
   * @param includeMetaColumn
   * @return
   */
  LinkedHashMap<String, DataType<?>> getFinalTableMetaColumns(boolean includeMetaColumn) {
    final LinkedHashMap<String, DataType<?>> metaColumns = new LinkedHashMap<>();
    metaColumns.put(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36).nullable(false));
    metaColumns.put(COLUMN_NAME_AB_EXTRACTED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    if (includeMetaColumn)
      metaColumns.put(COLUMN_NAME_AB_META, getSuperType().nullable(false));
    return metaColumns;
  }

  @Override
  public String createTable(final StreamConfig stream, final String suffix, final boolean force) {
    DSLContext dsl = getDslContext();
    CreateSchemaFinalStep createSchemaSql = createSchemaIfNotExists(quotedName(stream.id().finalNamespace()));

    // TODO: Use Naming transformer to sanitize these strings with redshift restrictions.
    String finalTableIdentifier = stream.id().finalName() + suffix.toLowerCase();
    CreateTableColumnStep createTableSql = dsl.createTable(quotedName(stream.id().finalNamespace(), finalTableIdentifier))
        .columns(buildFinalTableFields(stream.columns(), getFinalTableMetaColumns(true)));
    return createSchemaSql.getSQL() + ";" + System.lineSeparator() + createTableSql.getSQL() + ";";
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    // Check that the columns match, with special handling for the metadata columns.
    final LinkedHashMap<String, String> intendedColumns = stream.columns().entrySet().stream()
        .collect(LinkedHashMap::new,
            (map, column) -> map.put(column.getKey().name(), toDialectType(column.getValue()).getTypeName()),
            LinkedHashMap::putAll);
    final LinkedHashMap<String, String> actualColumns = existingTable.columns().entrySet().stream()
        .filter(column -> JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS.stream()
            .noneMatch(airbyteColumnName -> airbyteColumnName.equals(column.getKey())))
        .collect(LinkedHashMap::new,
            (map, column) -> map.put(column.getKey(), jdbcTypeNameFromRedshiftTypeName(column.getValue().type())),
            LinkedHashMap::putAll);

    final boolean sameColumns = actualColumns.equals(intendedColumns)
        && "varchar".equals(existingTable.columns().get(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID).type())
        && "timestamptz".equals(existingTable.columns().get(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT).type())
        && "super".equals(existingTable.columns().get(JavaBaseConstants.COLUMN_NAME_AB_META).type());

    return sameColumns;
  }

  @Override
  public String updateTable(final StreamConfig streamConfig,
                            final String finalSuffix,
                            final Optional<Instant> minRawTimestamp,
                            final boolean useExpensiveSaferCasting) {

    // TODO: Add flag to use merge vs insert/delete
    return insertAndDeleteTransaction(streamConfig, finalSuffix, minRawTimestamp, useExpensiveSaferCasting);

  }

  private String insertAndDeleteTransaction(final StreamConfig streamConfig,
                                            final String finalSuffix,
                                            final Optional<Instant> minRawTimestamp,
                                            final boolean useExpensiveSaferCasting) {
    final String finalSchema = streamConfig.id().finalNamespace();
    final String finalTable = streamConfig.id().finalName();
    final String rawSchema = streamConfig.id().rawNamespace();
    final String rawTable = streamConfig.id().rawName();

    // Poor person's guarantee of ordering of fields by using same source of ordered list of columns to
    // generate fields.
    final CommonTableExpression<Record> rawDataWithCasts = name("intermediate_data")
        .as(selectFromRawTable(rawSchema, rawTable, streamConfig.columns(), getFinalTableMetaColumns(false)));
    final Field<?> rowNumber = getRowNumber(streamConfig.primaryKey(), streamConfig.cursor());
    final CommonTableExpression<Record> filteredRows = name("numbered_rows").as(select(asterisk(), rowNumber).from(rawDataWithCasts));

    // Transactional insert and delete, Jooq only supports transaction starting 3.18
    // TODO: Complete this method.
    /*
     * return """ BEGIN; %s; %s; COMMIT; """.formatted(insertIntoFinalTable(...),
     * deleteFromFinalTable(...));
     */

    return insertIntoFinalTable(finalSchema, finalTable, streamConfig.columns(), getFinalTableMetaColumns(true))
        .select(with(rawDataWithCasts)
            .with(filteredRows)
            .select(buildFinalTableFields(streamConfig.columns(), getFinalTableMetaColumns(true)))
            .from(filteredRows)
            .where(field("row_number", Integer.class).eq(1)) // Can refer by CTE.field but no use since we don't strongly type them.
        )
        .getSQL(ParamType.INLINED);

  }

  private String mergeTransaction(final StreamConfig streamConfig,
                                  final String finalSuffix,
                                  final Optional<Instant> minRawTimestamp,
                                  final boolean useExpensiveSaferCasting) {

    throw new UnsupportedOperationException("Not implemented yet");

  }

  /**
   * Return ROW_NUMBER() OVER (PARTITION BY primaryKeys ORDER BY cursor DESC NULLS LAST,
   * _airbyte_extracted_at DESC)
   *
   * @param primaryKeys
   * @param cursor
   * @return
   */
  Field<?> getRowNumber(List<ColumnId> primaryKeys, Optional<ColumnId> cursor) {
    final List<Field<?>> primaryKeyFields = primaryKeys.stream().map(columnId -> field(quotedName(columnId.name()))).collect(Collectors.toList());
    final List<Field<?>> orderedFields = new ArrayList<>();
    // We can still use Jooq's field to get the quoted name with raw sql templating.
    // jooq's .desc returns SortField<?> instead of Field<?> and NULLS LAST doesn't work with it
    cursor.ifPresent(columnId -> orderedFields.add(field("{0} desc NULLS LAST", field(quotedName(columnId.name())))));
    orderedFields.add(field("{0} desc", quotedName(COLUMN_NAME_AB_EXTRACTED_AT)));
    return rowNumber()
        .over()
        .partitionBy(primaryKeyFields)
        .orderBy(orderedFields).as("row_number");
  }

  @VisibleForTesting
  SelectConditionStep<Record> selectFromRawTable(final String schemaName,
                                                 final String tableName,
                                                 final LinkedHashMap<ColumnId, AirbyteType> columns,
                                                 final Map<String, DataType<?>> metaColumns) {
    final DSLContext dsl = getDslContext();
    return dsl
        .select(buildRawTableSelectFields(columns, metaColumns))
        .select(buildAirbyteMetaColumn(columns))
        .from(table(quotedName(schemaName, tableName)))
        .where(field(name(COLUMN_NAME_AB_LOADED_AT)).isNull());
  }

  @VisibleForTesting
  InsertValuesStepN<Record> insertIntoFinalTable(final String schemaName,
                                                 final String tableName,
                                                 final LinkedHashMap<ColumnId, AirbyteType> columns,
                                                 final Map<String, DataType<?>> metaFields) {
    DSLContext dsl = getDslContext();
    return dsl
        .insertInto(table(quotedName(schemaName, tableName)))
        .columns(buildFinalTableFields(columns, metaFields));
  }

  @Override
  public String overwriteFinalTable(final StreamId stream, final String finalSuffix) {
    return Strings.join(
        List.of(
            DSL.dropTableIfExists(DSL.name(stream.finalNamespace(), stream.finalName())),
            DSL.alterTable(DSL.name(stream.finalNamespace(), stream.finalName() + finalSuffix))
                .renameTo(DSL.name(stream.finalName()))
                .getSQL()),
        ";" + System.lineSeparator());
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
        ";" + System.lineSeparator());
  }

  @Override
  public String clearLoadedAt(final StreamId streamId) {
    return DSL.update(DSL.table(DSL.name(streamId.rawNamespace(), streamId.rawName())))
        .set(DSL.field(COLUMN_NAME_AB_LOADED_AT), DSL.inline((String) null))
        .getSQL();
  }

  private static String jdbcTypeNameFromRedshiftTypeName(final String redshiftType) {
    return REDSHIFT_TYPE_NAME_TO_JDBC_TYPE.getOrDefault(redshiftType, redshiftType);
  }

}
