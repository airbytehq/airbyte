/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT;
import static io.airbyte.integrations.base.destination.typing_deduping.Sql.transactionally;
import static java.util.stream.Collectors.toList;
import static org.jooq.impl.DSL.alterTable;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.cast;
import static org.jooq.impl.DSL.dropTableIfExists;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.inline;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.noCondition;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.select;
import static org.jooq.impl.DSL.table;
import static org.jooq.impl.DSL.update;
import static org.jooq.impl.DSL.with;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Stream;
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
import org.jooq.impl.SQLDataType;

public abstract class JdbcSqlGenerator implements SqlGenerator<TableDefinition> {

  protected static final String ROW_NUMBER_COLUMN_NAME = "row_number";
  private static final String TYPING_CTE_ALIAS = "intermediate_data";
  private static final String NUMBERED_ROWS_CTE_ALIAS = "numbered_rows";

  protected final NamingConventionTransformer namingTransformer;
  protected final ColumnId cdcDeletedAtColumn;

  public JdbcSqlGenerator(final NamingConventionTransformer namingTransformer) {
    this.namingTransformer = namingTransformer;
    this.cdcDeletedAtColumn = buildColumnId("_ab_cdc_deleted_at");
  }

  @Override
  public StreamId buildStreamId(final String namespace, final String name, final String rawNamespaceOverride) {
    return new StreamId(
        namingTransformer.getNamespace(namespace),
        namingTransformer.convertStreamName(name),
        namingTransformer.getNamespace(rawNamespaceOverride),
        namingTransformer.convertStreamName(StreamId.concatenateRawTableName(namespace, name)),
        namespace,
        name);
  }

  @Override
  public ColumnId buildColumnId(final String name, final String suffix) {
    final String nameWithSuffix = name + suffix;
    return new ColumnId(
        namingTransformer.getIdentifier(nameWithSuffix),
        name,
        namingTransformer.getIdentifier(nameWithSuffix));
  }

  protected DataType<?> toDialectType(final AirbyteType type) {
    if (type instanceof final AirbyteProtocolType airbyteProtocolType) {
      return toDialectType(airbyteProtocolType);
    }
    return switch (type.getTypeName()) {
      case Struct.TYPE, UnsupportedOneOf.TYPE -> getStructType();
      case Array.TYPE -> getArrayType();
      // No nested Unions supported so this will definitely not result in infinite recursion.
      case Union.TYPE -> toDialectType(((Union) type).chooseType());
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
    };
  }

  @VisibleForTesting
  public DataType<?> toDialectType(final AirbyteProtocolType airbyteProtocolType) {
    return switch (airbyteProtocolType) {
      // Many destinations default to a very short length (e.g. Redshift defaults to 256).
      // Explicitly set 64KiB here. Subclasses may want to override this value.
      case STRING -> SQLDataType.VARCHAR(65535);
      // We default to precision=38, scale=9 across destinations.
      // This is the default numeric parameters for both redshift and bigquery.
      case NUMBER -> SQLDataType.DECIMAL(38, 9);
      case INTEGER -> SQLDataType.BIGINT;
      case BOOLEAN -> SQLDataType.BOOLEAN;
      case TIMESTAMP_WITH_TIMEZONE -> SQLDataType.TIMESTAMPWITHTIMEZONE;
      case TIMESTAMP_WITHOUT_TIMEZONE -> SQLDataType.TIMESTAMP;
      case TIME_WITH_TIMEZONE -> SQLDataType.TIMEWITHTIMEZONE;
      case TIME_WITHOUT_TIMEZONE -> SQLDataType.TIME;
      case DATE -> SQLDataType.DATE;
      case UNKNOWN -> getWidestType();
    };
  }

  protected abstract DataType<?> getStructType();

  protected abstract DataType<?> getArrayType();

  @VisibleForTesting
  public DataType<?> getTimestampWithTimeZoneType() {
    return toDialectType(AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
  }

  protected abstract DataType<?> getWidestType();

  protected abstract SQLDialect getDialect();

  /**
   * @param columns from the schema to be extracted from _airbyte_data column. Use the destination
   *        specific syntax to extract data
   * @param useExpensiveSaferCasting
   * @return a list of jooq fields for the final table insert statement.
   */
  protected abstract List<Field<?>> extractRawDataFields(final LinkedHashMap<ColumnId, AirbyteType> columns, boolean useExpensiveSaferCasting);

  /**
   *
   * @param columns from the schema to be used for type casting errors and construct _airbyte_meta
   *        column
   * @return
   */
  protected abstract Field<?> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> columns);

  /**
   * Get the cdc_deleted_at column condition for append_dedup mode by extracting it from _airbyte_data
   * column in raw table.
   *
   * @return
   */
  protected abstract Condition cdcDeletedAtNotNullCondition();

  /**
   * Get the window step function row_number() over (partition by primary_key order by cursor_field)
   * as row_number.
   *
   * @param primaryKey list of primary keys
   * @param cursorField cursor field used for ordering
   * @return
   */
  protected abstract Field<Integer> getRowNumber(final List<ColumnId> primaryKey, final Optional<ColumnId> cursorField);

  protected DSLContext getDslContext() {
    return DSL.using(getDialect());
  }

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
        metaColumns.entrySet().stream().map(metaColumn -> field(quotedName(metaColumn.getKey()), metaColumn.getValue())).collect(toList());
    final List<Field<?>> dataFields =
        columns.entrySet().stream().map(column -> field(quotedName(column.getKey().name()), toDialectType(column.getValue()))).collect(
            toList());
    dataFields.addAll(fields);
    return dataFields;
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
    metaColumns.put(COLUMN_NAME_AB_EXTRACTED_AT, getTimestampWithTimeZoneType().nullable(false));
    if (includeMetaColumn)
      metaColumns.put(COLUMN_NAME_AB_META, getStructType().nullable(false));
    return metaColumns;
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
  List<Field<?>> buildRawTableSelectFields(final LinkedHashMap<ColumnId, AirbyteType> columns,
                                           final Map<String, DataType<?>> metaColumns,
                                           final boolean useExpensiveSaferCasting) {
    final List<Field<?>> fields =
        metaColumns.entrySet().stream().map(metaColumn -> field(quotedName(metaColumn.getKey()), metaColumn.getValue())).collect(toList());
    // Use originalName with non-sanitized characters when extracting data from _airbyte_data
    final List<Field<?>> dataFields = extractRawDataFields(columns, useExpensiveSaferCasting);
    dataFields.addAll(fields);
    return dataFields;
  }

  @VisibleForTesting
  Condition rawTableCondition(final DestinationSyncMode syncMode, final boolean isCdcDeletedAtPresent, final Optional<Instant> minRawTimestamp) {
    Condition condition = field(name(COLUMN_NAME_AB_LOADED_AT)).isNull();
    if (syncMode == DestinationSyncMode.APPEND_DEDUP) {
      if (isCdcDeletedAtPresent) {
        condition = condition.or(cdcDeletedAtNotNullCondition());
      }
    }
    if (minRawTimestamp.isPresent()) {
      condition = condition.and(field(name(COLUMN_NAME_AB_EXTRACTED_AT)).gt(minRawTimestamp.get().toString()));
    }
    return condition;
  }

  @Override
  public Sql createSchema(final String schema) {
    return Sql.of(createSchemaSql(schema));
  }

  @Override
  public Sql createTable(final StreamConfig stream, final String suffix, final boolean force) {
    // TODO: Use Naming transformer to sanitize these strings with redshift restrictions.
    final String finalTableIdentifier = stream.id().finalName() + suffix.toLowerCase();
    if (!force) {
      return transactionally(Stream.concat(
          Stream.of(createTableSql(stream.id().finalNamespace(), finalTableIdentifier, stream.columns())),
          createIndexSql(stream, suffix).stream()).toList());
    }
    return transactionally(Stream.concat(
        Stream.of(
            dropTableIfExists(quotedName(stream.id().finalNamespace(), finalTableIdentifier)).getSQL(ParamType.INLINED),
            createTableSql(stream.id().finalNamespace(), finalTableIdentifier, stream.columns())),
        createIndexSql(stream, suffix).stream()).toList());
  }

  @Override
  public Sql updateTable(final StreamConfig streamConfig,
                         final String finalSuffix,
                         final Optional<Instant> minRawTimestamp,
                         final boolean useExpensiveSaferCasting) {

    // TODO: Add flag to use merge vs insert/delete
    return insertAndDeleteTransaction(streamConfig, finalSuffix, minRawTimestamp, useExpensiveSaferCasting);

  }

  @Override
  public Sql overwriteFinalTable(final StreamId stream, final String finalSuffix) {
    return transactionally(
        dropTableIfExists(name(stream.finalNamespace(), stream.finalName())).getSQL(ParamType.INLINED),
        alterTable(name(stream.finalNamespace(), stream.finalName() + finalSuffix))
            .renameTo(name(stream.finalName()))
            .getSQL());
  }

  @Override
  public Sql migrateFromV1toV2(final StreamId streamId, final String namespace, final String tableName) {
    final Name rawTableName = name(streamId.rawNamespace(), streamId.rawName());
    final DSLContext dsl = getDslContext();
    return transactionally(
        dsl.createSchemaIfNotExists(streamId.rawNamespace()).getSQL(),
        dsl.dropTableIfExists(rawTableName).getSQL(),
        DSL.createTable(rawTableName)
            .column(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36).nullable(false))
            .column(COLUMN_NAME_AB_EXTRACTED_AT, getTimestampWithTimeZoneType().nullable(false))
            .column(COLUMN_NAME_AB_LOADED_AT, getTimestampWithTimeZoneType().nullable(false))
            .column(COLUMN_NAME_DATA, getStructType().nullable(false))
            .as(select(
                field(COLUMN_NAME_AB_ID).as(COLUMN_NAME_AB_RAW_ID),
                field(COLUMN_NAME_EMITTED_AT).as(COLUMN_NAME_AB_EXTRACTED_AT),
                cast(null, getTimestampWithTimeZoneType()).as(COLUMN_NAME_AB_LOADED_AT),
                field(COLUMN_NAME_DATA).as(COLUMN_NAME_DATA)).from(table(name(namespace, tableName))))
            .getSQL(ParamType.INLINED));
  }

  @Override
  public Sql clearLoadedAt(final StreamId streamId) {
    return Sql.of(update(table(name(streamId.rawNamespace(), streamId.rawName())))
        .set(field(COLUMN_NAME_AB_LOADED_AT), inline((String) null))
        .getSQL());
  }

  @VisibleForTesting
  SelectConditionStep<Record> selectFromRawTable(final String schemaName,
                                                 final String tableName,
                                                 final LinkedHashMap<ColumnId, AirbyteType> columns,
                                                 final Map<String, DataType<?>> metaColumns,
                                                 final Condition condition,
                                                 final boolean useExpensiveSaferCasting) {
    final DSLContext dsl = getDslContext();
    return dsl
        .select(buildRawTableSelectFields(columns, metaColumns, useExpensiveSaferCasting))
        .select(buildAirbyteMetaColumn(columns))
        .from(table(quotedName(schemaName, tableName)))
        .where(condition);
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

  private Sql insertAndDeleteTransaction(final StreamConfig streamConfig,
                                         final String finalSuffix,
                                         final Optional<Instant> minRawTimestamp,
                                         final boolean useExpensiveSaferCasting) {
    final String finalSchema = streamConfig.id().finalNamespace();
    final String finalTable = streamConfig.id().finalName() + (finalSuffix != null ? finalSuffix.toLowerCase() : "");
    final String rawSchema = streamConfig.id().rawNamespace();
    final String rawTable = streamConfig.id().rawName();

    // Poor person's guarantee of ordering of fields by using same source of ordered list of columns to
    // generate fields.
    final CommonTableExpression<Record> rawTableRowsWithCast = name(TYPING_CTE_ALIAS).as(
        selectFromRawTable(rawSchema, rawTable, streamConfig.columns(),
            getFinalTableMetaColumns(false),
            rawTableCondition(streamConfig.destinationSyncMode(),
                streamConfig.columns().containsKey(cdcDeletedAtColumn),
                minRawTimestamp),
            useExpensiveSaferCasting));
    final List<Field<?>> finalTableFields = buildFinalTableFields(streamConfig.columns(), getFinalTableMetaColumns(true));
    final Field<Integer> rowNumber = getRowNumber(streamConfig.primaryKey(), streamConfig.cursor());
    final CommonTableExpression<Record> filteredRows = name(NUMBERED_ROWS_CTE_ALIAS).as(
        select(asterisk(), rowNumber).from(rawTableRowsWithCast));

    // Used for append-dedupe mode.
    final String insertStmtWithDedupe =
        insertIntoFinalTable(finalSchema, finalTable, streamConfig.columns(), getFinalTableMetaColumns(true))
            .select(with(rawTableRowsWithCast)
                .with(filteredRows)
                .select(finalTableFields)
                .from(filteredRows)
                .where(field(name(ROW_NUMBER_COLUMN_NAME), Integer.class).eq(1)) // Can refer by CTE.field but no use since we don't strongly type
                                                                                 // them.
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
        streamConfig.columns().containsKey(cdcDeletedAtColumn) ? deleteFromFinalTableCdcDeletes(finalSchema, finalTable) : "";
    final String checkpointStmt = checkpointRawTable(rawSchema, rawTable, minRawTimestamp);

    if (streamConfig.destinationSyncMode() != DestinationSyncMode.APPEND_DEDUP) {
      return transactionally(
          insertStmt,
          checkpointStmt);
    }

    // For append-dedupe
    return transactionally(
        insertStmtWithDedupe,
        deleteStmt,
        deleteCdcDeletesStmt,
        checkpointStmt);
  }

  private String mergeTransaction(final StreamConfig streamConfig,
                                  final String finalSuffix,
                                  final Optional<Instant> minRawTimestamp,
                                  final boolean useExpensiveSaferCasting) {

    throw new UnsupportedOperationException("Not implemented yet");

  }

  protected String createSchemaSql(final String namespace) {
    final DSLContext dsl = getDslContext();
    final CreateSchemaFinalStep createSchemaSql = dsl.createSchemaIfNotExists(quotedName(namespace));
    return createSchemaSql.getSQL();
  }

  protected String createTableSql(final String namespace, final String tableName, final LinkedHashMap<ColumnId, AirbyteType> columns) {
    final DSLContext dsl = getDslContext();
    final CreateTableColumnStep createTableSql = dsl
        .createTable(quotedName(namespace, tableName))
        .columns(buildFinalTableFields(columns, getFinalTableMetaColumns(true)));
    return createTableSql.getSQL();
  }

  /**
   * Subclasses may override this method to add additional indexes after their CREATE TABLE statement.
   * This is useful if the destination's CREATE TABLE statement does not accept an index definition.
   */
  protected List<String> createIndexSql(final StreamConfig stream, final String suffix) {
    return Collections.emptyList();
  }

  protected String beginTransaction() {
    return "BEGIN";
  }

  protected String commitTransaction() {
    return "COMMIT";
  }

  private String commitTransactionInternal() {
    return commitTransaction() + ";";
  }

  private String deleteFromFinalTable(final String schemaName,
                                      final String tableName,
                                      final List<ColumnId> primaryKeys,
                                      final Optional<ColumnId> cursor) {
    final DSLContext dsl = getDslContext();
    // Unknown type doesn't play well with where .. in (select..)
    final Field<Object> airbyteRawId = field(quotedName(COLUMN_NAME_AB_RAW_ID));
    final Field<Integer> rowNumber = getRowNumber(primaryKeys, cursor);
    return dsl.deleteFrom(table(quotedName(schemaName, tableName)))
        .where(airbyteRawId.in(
            select(airbyteRawId)
                .from(select(airbyteRawId, rowNumber)
                    .from(table(quotedName(schemaName, tableName))).asTable("airbyte_ids"))
                .where(field(name(ROW_NUMBER_COLUMN_NAME)).ne(1))))
        .getSQL(ParamType.INLINED);
  }

  private String deleteFromFinalTableCdcDeletes(final String schema, final String tableName) {
    final DSLContext dsl = getDslContext();
    return dsl.deleteFrom(table(quotedName(schema, tableName)))
        .where(field(quotedName(cdcDeletedAtColumn.name())).isNotNull())
        .getSQL(ParamType.INLINED);
  }

  private String checkpointRawTable(final String schemaName, final String tableName, final Optional<Instant> minRawTimestamp) {
    final DSLContext dsl = getDslContext();
    Condition extractedAtCondition = noCondition();
    if (minRawTimestamp.isPresent()) {
      extractedAtCondition = extractedAtCondition.and(field(name(COLUMN_NAME_AB_EXTRACTED_AT)).gt(minRawTimestamp.get().toString()));
    }
    return dsl.update(table(quotedName(schemaName, tableName)))
        .set(field(quotedName(COLUMN_NAME_AB_LOADED_AT)), currentTimestamp())
        .where(field(quotedName(COLUMN_NAME_AB_LOADED_AT)).isNull()).and(extractedAtCondition)
        .getSQL(ParamType.INLINED);
  }

  protected Field<?> castedField(
                                 final Field<?> field,
                                 final AirbyteType type,
                                 final String alias,
                                 final boolean useExpensiveSaferCasting) {
    if (type instanceof final AirbyteProtocolType airbyteProtocolType) {
      return castedField(field, airbyteProtocolType, useExpensiveSaferCasting).as(quotedName(alias));
    }

    // Redshift SUPER can silently cast an array type to struct and vice versa.
    return switch (type.getTypeName()) {
      case Struct.TYPE, UnsupportedOneOf.TYPE -> cast(field, getStructType()).as(quotedName(alias));
      case Array.TYPE -> cast(field, getArrayType()).as(quotedName(alias));
      // No nested Unions supported so this will definitely not result in infinite recursion.
      case Union.TYPE -> castedField(field, ((Union) type).chooseType(), alias, useExpensiveSaferCasting);
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
    };
  }

  protected Field<?> castedField(final Field<?> field, final AirbyteProtocolType type, final boolean useExpensiveSaferCasting) {
    return cast(field, toDialectType(type));
  }

  protected Field<Timestamp> currentTimestamp() {
    return DSL.currentTimestamp();
  }

}
