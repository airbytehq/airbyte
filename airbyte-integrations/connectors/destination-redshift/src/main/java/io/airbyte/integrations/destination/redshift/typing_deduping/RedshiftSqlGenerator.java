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
import static org.jooq.impl.DSL.alterTable;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.cast;
import static org.jooq.impl.DSL.createSchemaIfNotExists;
import static org.jooq.impl.DSL.dropTableIfExists;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.function;
import static org.jooq.impl.DSL.inline;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.noCondition;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.rowNumber;
import static org.jooq.impl.DSL.select;
import static org.jooq.impl.DSL.table;
import static org.jooq.impl.DSL.update;
import static org.jooq.impl.DSL.val;
import static org.jooq.impl.DSL.with;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
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
import io.airbyte.protocol.models.v0.DestinationSyncMode;
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
import org.jooq.impl.DSL;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;

public class RedshiftSqlGenerator extends JdbcSqlGenerator {

  public static final String CASE_STATEMENT_SQL_TEMPLATE = "CASE WHEN {0} THEN {1} ELSE {2} END ";
  public static final String CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE = "CASE WHEN {0} THEN {1} END ";
  private static final Map<String, String> REDSHIFT_TYPE_NAME_TO_JDBC_TYPE = ImmutableMap.of(
      "numeric", "decimal",
      "int8", "bigint",
      "bool", "boolean",
      "timestamptz", "timestamp with time zone",
      "timetz", "time with time zone");
  private static final String COLUMN_ERROR_MESSAGE_FORMAT = "Problem with `%s`";
  private static final String AIRBYTE_META_COLUMN_ERRORS_KEY = "errors";

  private final ColumnId CDC_DELETED_AT_COLUMN = buildColumnId("_ab_cdc_deleted_at");

  public RedshiftSqlGenerator(final NamingConventionTransformer namingTransformer) {
    super(namingTransformer);
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

  @Override
  protected SQLDialect getDialect() {
    return SQLDialect.POSTGRES;
  }

  protected DSLContext getDslContext() {
    return DSL.using(getDialect());
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
    // Use originalName with non-sanitized characters when extracting data from _airbyte_data
    final List<Field<?>> dataFields = columns
        .entrySet()
        .stream()
        .map(column -> castedField(field(quotedName(COLUMN_NAME_DATA, column.getKey().originalName())), column.getValue(), column.getKey().name()))
        .collect(Collectors.toList());
    dataFields.addAll(fields);
    return dataFields;
  }

  private Field<?> castedField(final Field<?> field, final AirbyteType type, final String alias) {
    if (type instanceof final AirbyteProtocolType airbyteProtocolType) {
      switch (airbyteProtocolType) {
        case STRING -> {
          return field(CASE_STATEMENT_SQL_TEMPLATE,
              jsonTypeOf(field).ne("string").and(field.isNotNull()),
              jsonSerialize(field),
              castedField(field, airbyteProtocolType)).as(quotedName(alias));
        }
        default -> {
          return castedField(field, airbyteProtocolType).as(quotedName(alias));
        }
      }

    }
    // Redshift SUPER can silently cast an array type to struct and vice versa.
    return switch (type.getTypeName()) {
      case Struct.TYPE, UnsupportedOneOf.TYPE -> field(CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE,
          jsonTypeOf(field).eq("object"),
          cast(field, getStructType())).as(quotedName(alias));
      case Array.TYPE -> field(CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE,
          jsonTypeOf(field).eq("array"),
          cast(field, getArrayType())).as(quotedName(alias));
      // No nested Unions supported so this will definitely not result in infinite recursion.
      case Union.TYPE -> castedField(field, ((Union) type).chooseType(), alias);
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
    };
  }

  private Field<?> castedField(final Field<?> field, final AirbyteProtocolType type) {
    return cast(field, toDialectType(type));
  }

  private Field<String> jsonTypeOf(final Field<?> field) {
    return function("JSON_TYPEOF", SQLDataType.VARCHAR, field);
  }

  private Field<String> jsonSerialize(final Field<?> field) {
    return function("JSON_SERIALIZE", SQLDataType.VARCHAR, field);
  }

  /**
   * Redshift ARRAY_CONCAT supports only 2 arrays, recursively build ARRAY_CONCAT for n arrays.
   *
   * @param arrays
   * @return
   */
  Field<?> arrayConcatStmt(final List<Field<?>> arrays) {
    if (arrays.isEmpty()) {
      return field("ARRAY()"); // Return an empty string if the list is empty
    }

    // Base case: if there's only one element, return it
    if (arrays.size() == 1) {
      return arrays.get(0);
    }

    // Recursive case: construct ARRAY_CONCAT function call
    final Field<?> lastValue = arrays.get(arrays.size() - 1);
    final Field<?> recursiveCall = arrayConcatStmt(arrays.subList(0, arrays.size() - 1));

    return function("ARRAY_CONCAT", getSuperType(), recursiveCall, lastValue);
  }

  Field<?> toCastingErrorCaseStmt(final ColumnId column, final AirbyteType type) {
    final Field<?> field = field(quotedName(COLUMN_NAME_DATA, column.originalName()));
    // Just checks if data is not null but casted data is null. This also accounts for conditional
    // casting result of array and struct.
    // TODO: Timestamp format issues can result in null values when cast, add regex check if destination
    // supports regex functions.
    return field(CASE_STATEMENT_SQL_TEMPLATE,
        field.isNotNull().and(castedField(field, type, column.name()).isNull()),
        function("ARRAY", getSuperType(), val(COLUMN_ERROR_MESSAGE_FORMAT.formatted(column.name()))), field("ARRAY()"));
  }

  Field<?> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> columns) {
    final List<Field<?>> dataFields = columns
        .entrySet()
        .stream()
        .map(column -> toCastingErrorCaseStmt(column.getKey(), column.getValue()))
        .collect(Collectors.toList());
    return function("OBJECT", getSuperType(), val(AIRBYTE_META_COLUMN_ERRORS_KEY), arrayConcatStmt(dataFields)).as(COLUMN_NAME_AB_META);

  }

  /**
   * Use this method to get the final table meta columns with or without _airbyte_meta column.
   *
   * @param includeMetaColumn
   * @return
   */
  LinkedHashMap<String, DataType<?>> getFinalTableMetaColumns(final boolean includeMetaColumn) {
    final LinkedHashMap<String, DataType<?>> metaColumns = new LinkedHashMap<>();
    metaColumns.put(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36).nullable(false));
    metaColumns.put(COLUMN_NAME_AB_EXTRACTED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    if (includeMetaColumn)
      metaColumns.put(COLUMN_NAME_AB_META, getSuperType().nullable(false));
    return metaColumns;
  }

  @Override
  public String createTable(final StreamConfig stream, final String suffix, final boolean force) {
    final DSLContext dsl = getDslContext();
    final CreateSchemaFinalStep createSchemaSql = createSchemaIfNotExists(quotedName(stream.id().finalNamespace()));

    // TODO: Use Naming transformer to sanitize these strings with redshift restrictions.
    final String finalTableIdentifier = stream.id().finalName() + suffix.toLowerCase();
    final CreateTableColumnStep createTableSql = dsl
        .createTable(quotedName(stream.id().finalNamespace(), finalTableIdentifier))
        .columns(buildFinalTableFields(stream.columns(), getFinalTableMetaColumns(true)));
    if (!force) {
      return Strings.join(
          List.of(
              createSchemaSql.getSQL() + ";",
              // Redshift doesn't care about primary key but we can use SORTKEY for performance, its a table
              // attribute not supported by jooq.
              createTableSql.getSQL() + System.lineSeparator() + " SORTKEY(\"" + COLUMN_NAME_AB_EXTRACTED_AT + "\");"),
          System.lineSeparator());
    }
    return Strings.join(
        List.of(
            createSchemaSql.getSQL() + ";",
            "BEGIN;",
            dropTableIfExists(quotedName(stream.id().finalNamespace(), finalTableIdentifier)) + ";",
            createTableSql.getSQL() + System.lineSeparator() + " SORTKEY(\"" + COLUMN_NAME_AB_EXTRACTED_AT + "\");",
            "COMMIT;"),
        System.lineSeparator());
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
    final String finalTable = streamConfig.id().finalName() + (finalSuffix != null ? finalSuffix.toLowerCase() : "");
    final String rawSchema = streamConfig.id().rawNamespace();
    final String rawTable = streamConfig.id().rawName();

    // Poor person's guarantee of ordering of fields by using same source of ordered list of columns to
    // generate fields.
    final CommonTableExpression<Record> rawTableRowsWithCast = name("intermediate_data").as(
        selectFromRawTable(rawSchema, rawTable, streamConfig.columns(),
            getFinalTableMetaColumns(false),
            rawTableCondition(streamConfig.destinationSyncMode(),
                streamConfig.columns().containsKey(CDC_DELETED_AT_COLUMN),
                minRawTimestamp)));
    final List<Field<?>> finalTableFields = buildFinalTableFields(streamConfig.columns(), getFinalTableMetaColumns(true));
    final Field<Integer> rowNumber = getRowNumber(streamConfig.primaryKey(), streamConfig.cursor());
    final CommonTableExpression<Record> filteredRows = name("numbered_rows").as(
        select(asterisk(), rowNumber).from(rawTableRowsWithCast));

    // Used for append-dedupe mode.
    final String insertStmtWithDedupe =
        insertIntoFinalTable(finalSchema, finalTable, streamConfig.columns(), getFinalTableMetaColumns(true))
            .select(with(rawTableRowsWithCast)
                .with(filteredRows)
                .select(finalTableFields)
                .from(filteredRows)
                .where(field("row_number", Integer.class).eq(1)) // Can refer by CTE.field but no use since we don't strongly type them.
            )
            .getSQL(ParamType.INLINED);

    // Used for append and overwrite modes.
    final String insertStmt =
        insertIntoFinalTable(finalSchema, finalTable, streamConfig.columns(), getFinalTableMetaColumns(true))
            .select(with(rawTableRowsWithCast)
                .select(finalTableFields)
                .from(rawTableRowsWithCast))
            .getSQL(ParamType.INLINED);
    final String deleteStmt = deleteFromFinalTable(finalSchema, finalTable, streamConfig.primaryKey(), streamConfig.cursor());
    final String deleteCdcDeletesStmt =
        streamConfig.columns().containsKey(CDC_DELETED_AT_COLUMN) ? deleteFromFinalTableCdcDeletes(finalSchema, finalTable) : "";
    final String checkpointStmt = checkpointRawTable(rawSchema, rawTable, minRawTimestamp);

    if (streamConfig.destinationSyncMode() != DestinationSyncMode.APPEND_DEDUP) {
      return Strings.join(
          List.of(
              "BEGIN",
              insertStmt,
              checkpointStmt,
              "COMMIT;"),
          ";" + System.lineSeparator());
    }

    // For append-dedupe
    return Strings.join(
        List.of(
            "BEGIN",
            insertStmtWithDedupe,
            deleteStmt,
            deleteCdcDeletesStmt,
            checkpointStmt,
            "COMMIT;"),
        ";" + System.lineSeparator());
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
  Field<Integer> getRowNumber(final List<ColumnId> primaryKeys, final Optional<ColumnId> cursor) {
    final List<Field<?>> primaryKeyFields =
        primaryKeys != null ? primaryKeys.stream().map(columnId -> field(quotedName(columnId.name()))).collect(Collectors.toList())
            : new ArrayList<>();
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
                                                 final Map<String, DataType<?>> metaColumns,
                                                 final Condition condition) {
    final DSLContext dsl = getDslContext();
    return dsl
        .select(buildRawTableSelectFields(columns, metaColumns))
        .select(buildAirbyteMetaColumn(columns))
        .from(table(quotedName(schemaName, tableName)))
        .where(condition);
  }

  Condition rawTableCondition(final DestinationSyncMode syncMode, final boolean isCdcDeletedAtPresent, final Optional<Instant> minRawTimestamp) {
    Condition condition = field(name(COLUMN_NAME_AB_LOADED_AT)).isNull();
    if (syncMode == DestinationSyncMode.APPEND_DEDUP) {
      if (isCdcDeletedAtPresent) {
        condition = condition.or(field(name(COLUMN_NAME_AB_LOADED_AT)).isNotNull()
            .and(function("JSON_TYPEOF", SQLDataType.VARCHAR, field(quotedName(COLUMN_NAME_DATA, CDC_DELETED_AT_COLUMN.name())))
                .ne("null")));
      }
    }
    if (minRawTimestamp.isPresent()) {
      condition = condition.and(field(name(COLUMN_NAME_AB_EXTRACTED_AT)).gt(minRawTimestamp.get().toString()));
    }
    return condition;
  }

  @VisibleForTesting
  InsertValuesStepN<Record> insertIntoFinalTable(final String schemaName,
                                                 final String tableName,
                                                 final LinkedHashMap<ColumnId, AirbyteType> columns,
                                                 final Map<String, DataType<?>> metaFields) {
    final DSLContext dsl = getDslContext();
    return dsl
        .insertInto(table(quotedName(schemaName, tableName)))
        .columns(buildFinalTableFields(columns, metaFields));
  }

  String deleteFromFinalTable(final String schemaName, final String tableName, final List<ColumnId> primaryKeys, final Optional<ColumnId> cursor) {
    final DSLContext dsl = getDslContext();
    // Unknown type doesn't play well with where .. in (select..)
    final Field<Object> airbyteRawId = field(quotedName(COLUMN_NAME_AB_RAW_ID));
    final Field<Integer> rowNumber = getRowNumber(primaryKeys, cursor);
    return dsl.deleteFrom(table(quotedName(schemaName, tableName)))
        .where(airbyteRawId.in(
            select(airbyteRawId)
                .from(select(airbyteRawId, rowNumber)
                    .from(table(quotedName(schemaName, tableName))).asTable("airbyte_ids"))
                .where(field("row_number").ne(1))))
        .getSQL(ParamType.INLINED);
  }

  String deleteFromFinalTableCdcDeletes(final String schema, final String tableName) {
    final DSLContext dsl = getDslContext();
    return dsl.deleteFrom(table(quotedName(schema, tableName)))
        .where(field(quotedName(CDC_DELETED_AT_COLUMN.name())).isNotNull())
        .getSQL(ParamType.INLINED);
  }

  String checkpointRawTable(final String schemaName, final String tableName, final Optional<Instant> minRawTimestamp) {
    final DSLContext dsl = getDslContext();
    Condition extractedAtCondition = noCondition();
    if (minRawTimestamp.isPresent()) {
      extractedAtCondition = extractedAtCondition.and(field(name(COLUMN_NAME_AB_EXTRACTED_AT)).gt(minRawTimestamp.get().toString()));
    }
    return dsl.update(table(quotedName(schemaName, tableName)))
        .set(field(quotedName(COLUMN_NAME_AB_LOADED_AT), SQLDataType.TIMESTAMPWITHTIMEZONE),
            function("GETDATE", SQLDataType.TIMESTAMPWITHTIMEZONE))
        .where(field(quotedName(COLUMN_NAME_AB_LOADED_AT)).isNull()).and(extractedAtCondition)
        .getSQL(ParamType.INLINED);
  }

  @Override
  public String overwriteFinalTable(final StreamId stream, final String finalSuffix) {
    return Strings.join(
        List.of(
            dropTableIfExists(name(stream.finalNamespace(), stream.finalName())),
            alterTable(name(stream.finalNamespace(), stream.finalName() + finalSuffix))
                .renameTo(name(stream.finalName()))
                .getSQL()),
        ";" + System.lineSeparator());
  }

  @Override
  public String migrateFromV1toV2(final StreamId streamId, final String namespace, final String tableName) {
    final Name rawTableName = name(streamId.rawNamespace(), streamId.rawName());
    return Strings.join(
        List.of(
            createSchemaIfNotExists(streamId.rawNamespace()).getSQL(),
            dropTableIfExists(rawTableName).getSQL(),
            DSL.createTable(rawTableName)
                .column(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36).nullable(false))
                .column(COLUMN_NAME_AB_EXTRACTED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false))
                .column(COLUMN_NAME_AB_LOADED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false))
                .column(COLUMN_NAME_DATA, getSuperType().nullable(false))
                .as(select(
                    field(COLUMN_NAME_AB_ID).as(COLUMN_NAME_AB_RAW_ID),
                    field(COLUMN_NAME_EMITTED_AT).as(COLUMN_NAME_AB_EXTRACTED_AT),
                    cast(null, SQLDataType.TIMESTAMPWITHTIMEZONE).as(COLUMN_NAME_AB_LOADED_AT),
                    field(COLUMN_NAME_DATA).as(COLUMN_NAME_DATA)).from(table(name(namespace, tableName))))
                .getSQL(ParamType.INLINED)),
        ";" + System.lineSeparator());
  }

  @Override
  public String clearLoadedAt(final StreamId streamId) {
    return update(table(name(streamId.rawNamespace(), streamId.rawName())))
        .set(field(COLUMN_NAME_AB_LOADED_AT), inline((String) null))
        .getSQL();
  }

  @Override
  public boolean shouldRetry(final Exception e) {
    return false;
  }

  private static String jdbcTypeNameFromRedshiftTypeName(final String redshiftType) {
    return REDSHIFT_TYPE_NAME_TO_JDBC_TYPE.getOrDefault(redshiftType, redshiftType);
  }

}
