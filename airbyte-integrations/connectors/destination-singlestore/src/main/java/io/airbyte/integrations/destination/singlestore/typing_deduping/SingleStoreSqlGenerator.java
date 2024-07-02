/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.*;
import static io.airbyte.integrations.base.destination.typing_deduping.Sql.separately;
import static io.airbyte.integrations.base.destination.typing_deduping.Sql.transactionally;
import static io.airbyte.integrations.destination.singlestore.typing_deduping.DslUtils.extractColumnAsString;
import static org.jooq.impl.DSL.*;
import static org.jooq.impl.SQLDataType.BOOLEAN;
import static org.jooq.impl.SQLDataType.VARCHAR;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.*;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.time.Instant;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.jooq.*;
import org.jooq.conf.ParamType;
import org.jooq.impl.DSL;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreSqlGenerator extends JdbcSqlGenerator {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreSqlGenerator.class);

  public static final DataType<Object> JSON_TYPE = new DefaultDataType<>(SQLDialect.DEFAULT, Object.class, "json");

  public static final String CASE_STATEMENT_SQL_TEMPLATE = "CASE WHEN {0} THEN {1} ELSE {2} END ";
  private static final String META_COLUMN_WARNINGS_KEY = "warnings";
  private static final String TYPING_CTE_ALIAS = "intermediate_data";
  private static final String NUMBERED_ROWS_CTE_ALIAS = "numbered_rows";

  private final JsonNode config;

  public SingleStoreSqlGenerator(final NamingConventionTransformer namingTransformer, JsonNode config) {
    super(namingTransformer, false);
    this.config = config;
  }

  @NotNull
  @Override
  public StreamId buildStreamId(final @NotNull String namespace, final @NotNull String name, final @NotNull String rawNamespaceOverride) {
    final String streamName = getNamingTransformer().getIdentifier(StreamId.concatenateRawTableName(namespace, name));
    return new StreamId(
        getNamingTransformer().getNamespace(namespace),
        getNamingTransformer().convertStreamName(name),
        getNamingTransformer().getNamespace(rawNamespaceOverride).toLowerCase(),
        streamName,
        namespace,
        name);
  }

  @NotNull
  @Override
  protected DataType<?> getStructType() {
    return JSON_TYPE;
  }

  @Override
  protected DataType<?> getArrayType() {
    return JSON_TYPE;
  }

  @Override
  protected DataType<?> getWidestType() {
    return JSON_TYPE;
  }

  // Use MySQL dialect as most suitable for SingleStore.
  @Override
  public SQLDialect getDialect() {
    return SQLDialect.MYSQL;
  }

  @NotNull
  @Override
  public DataType<?> toDialectType(@NotNull AirbyteProtocolType airbyteProtocolType) {
    return switch (airbyteProtocolType) {
      case AirbyteProtocolType.STRING -> VARCHAR(21844);
      case AirbyteProtocolType.NUMBER -> SQLDataType.DECIMAL(38, 9);
      case AirbyteProtocolType.INTEGER -> SQLDataType.BIGINT;
      case AirbyteProtocolType.BOOLEAN -> SQLDataType.BOOLEAN;
      case AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE, AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE -> SQLDataType.TIMESTAMP(6);
      case AirbyteProtocolType.TIME_WITHOUT_TIMEZONE, AirbyteProtocolType.TIME_WITH_TIMEZONE -> SQLDataType.TIME(6);
      case AirbyteProtocolType.DATE -> SQLDataType.DATE;
      case AirbyteProtocolType.UNKNOWN -> Objects.requireNonNull(getWidestType());
    };
  }

  @NotNull
  @Override
  public Sql createTable(@NotNull final StreamConfig stream, @NotNull final String suffix, final boolean force) {
    final List<Sql> statements = new ArrayList<>();
    final Name finalTableName = unquotedName(stream.getId().getFinalNamespace(), stream.getId().getFinalName() + suffix);
    final String idxName = stream.getId().getFinalName() + suffix + "_%s_idx";
    statements.add(super.createTable(stream, suffix, force));
    if (stream.getDestinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      statements.add(Sql.of(getDslContext().createIndex(unquotedName(stream.getId().getFinalName() + suffix + "pk_idx"))
          .on(unquotedName(stream.getId().getFinalNamespace(), stream.getId().getFinalName() + suffix),
              stream.getPrimaryKey().stream().map(pk -> unquotedName(pk.getName())).toList())
          .getSQL()));
      final List<Name> pkNames = stream.getPrimaryKey().stream()
          .map(pk -> unquotedName(pk.getName()))
          .toList();
      statements.add(Sql.of(getDslContext().createIndex(unquotedName(String.format(idxName, "pk_cursor_" + COLUMN_NAME_AB_EXTRACTED_AT))).on(
          finalTableName,
          Stream.of(
              pkNames.stream(),
              stream.getCursor().stream().map(cursor -> unquotedName(cursor.getName())),
              Stream.of(unquotedName(COLUMN_NAME_AB_EXTRACTED_AT))).flatMap(Function.identity()).collect(Collectors.toSet()))
          .getSQL()));
    }
    statements.add(Sql.of(getDslContext().createIndex(unquotedName(String.format(idxName, COLUMN_NAME_AB_EXTRACTED_AT))).on(
        finalTableName,
        unquotedName(COLUMN_NAME_AB_EXTRACTED_AT))
        .getSQL()));
    statements.add(Sql.of(getDslContext().createIndex(unquotedName(String.format(idxName, COLUMN_NAME_AB_RAW_ID))).on(
        finalTableName,
        unquotedName(COLUMN_NAME_AB_RAW_ID))
        .getSQL()));
    return Sql.concat(statements);
  }

  @NotNull
  @Override
  public Sql updateTable(@NotNull StreamConfig streamConfig,
                         @NotNull String finalSuffix,
                         @NotNull Optional<Instant> minRawTimestamp,
                         boolean useExpensiveSaferCasting) {
    final var finalSchema = streamConfig.getId().getFinalNamespace();
    final var finalTable =
        streamConfig.getId().getFinalName() + finalSuffix.toLowerCase(Locale.getDefault());
    final var rawSchema = streamConfig.getId().getRawNamespace();
    final var rawTable = streamConfig.getId().getRawName();
    final var destinationMode = streamConfig.getDestinationSyncMode();
    var rawTableRowsWithCast =
        DSL.name(TYPING_CTE_ALIAS).as(selectFromRawTable(
            rawSchema,
            rawTable,
            Objects.requireNonNull(streamConfig.getColumns()),
            getFinalTableMetaColumns(false),
            rawTableCondition(
                Objects.requireNonNull(destinationMode),
                streamConfig.getColumns().containsKey(getCdcDeletedAtColumn()),
                minRawTimestamp),
            useExpensiveSaferCasting));
    var finalTableFields =
        buildFinalTableFields(streamConfig.getColumns(), getFinalTableMetaColumns(true));
    var rowNumber = getRowNumber(streamConfig.getPrimaryKey(), Objects.requireNonNull(streamConfig.getCursor()));
    var filteredRows =
        DSL.name(NUMBERED_ROWS_CTE_ALIAS).as(DSL.select(DSL.asterisk(), rowNumber).from(rawTableRowsWithCast));
    var insertStmtWithDedupe =
        insertIntoFinalTable(
            finalSchema,
            finalTable,
            streamConfig.getColumns(),
            getFinalTableMetaColumns(true))
                .select(
                    DSL.with(rawTableRowsWithCast)
                        .with(filteredRows)
                        .select(finalTableFields)
                        .from(filteredRows)
                        .where(
                            DSL.field(DSL.name(ROW_NUMBER_COLUMN_NAME), Integer.class).eq(1)))
                .getSQL(ParamType.INLINED);
    // Used for append and overwrite modes.
    var insertStmt =
        insertIntoFinalTable(
            finalSchema,
            finalTable,
            streamConfig.getColumns(),
            getFinalTableMetaColumns(true))
                .select(
                    DSL.with(rawTableRowsWithCast)
                        .select(finalTableFields)
                        .from(rawTableRowsWithCast))
                .getSQL(ParamType.INLINED);
    var deleteStmt =
        deleteFromFinalTable(
            finalSchema,
            finalTable,
            Objects.requireNonNull(streamConfig.getPrimaryKey()),
            streamConfig.getCursor());
    var checkpointStmt = checkpointRawTable(rawSchema, rawTable, minRawTimestamp);
    if (destinationMode != DestinationSyncMode.APPEND_DEDUP) {
      if (Objects.equals(rawSchema, finalSchema)) {
        return transactionally(insertStmt, checkpointStmt);
      } else {
        LOGGER.warn("May cause inconsistent migration status. For safe integration use the same database for raw and final tables.");
        return separately(insertStmt, checkpointStmt);
      }
    }
    String deleteCdcDeletesStmt = "";
    if (streamConfig.getColumns().containsKey(getCdcDeletedAtColumn())) {
      deleteCdcDeletesStmt = getDslContext().deleteFrom(DSL.table(DSL.quotedName(finalSchema, finalTable)))
          .where(DSL.field(DSL.quotedName(getCdcDeletedAtColumn().getName())).isNotNull())
          .getSQL(ParamType.INLINED);
    }
    // For append-dedupe
    if (Objects.equals(rawSchema, finalSchema)) {
      return transactionally(
          insertStmtWithDedupe,
          deleteStmt,
          deleteCdcDeletesStmt,
          checkpointStmt);
    } else {
      LOGGER.warn("May cause inconsistent migration state. For safe integration use same the database for raw and final tables.");
      var finalTableStatements = transactionally(insertStmtWithDedupe, deleteStmt, deleteCdcDeletesStmt);
      var checkPoint = transactionally(checkpointStmt);
      return Sql.concat(finalTableStatements, checkPoint);
    }
  }

  @NotNull
  @Override
  protected List<Field<?>> extractRawDataFields(@NotNull LinkedHashMap<ColumnId, AirbyteType> columns, boolean useExpensiveSaferCasting) {
    return columns.entrySet().stream()
        .map(column -> column.getValue() == AirbyteProtocolType.STRING
            ? extractColumnAsString(column.getKey()).as(DSL.quotedName(column.getKey().getName()))
            : castedField(extractColumnAsString(column.getKey()), column.getValue(), column.getKey().getName(), useExpensiveSaferCasting))
        .collect(Collectors.toList());
  }

  @NotNull
  private Field<?> castedField(@Nullable Field<?> field, @NotNull AirbyteType type, @Nullable String alias, boolean useSaferCasting) {
    if (type instanceof AirbyteProtocolType) {
      return castedField(field, (AirbyteProtocolType) type, useSaferCasting).as(DSL.quotedName(alias));
    }

    switch (type.getTypeName()) {
      case Struct.TYPE, UnsupportedOneOf.TYPE -> {
        return DslUtils.cast(field, getStructType(), useSaferCasting).as(DSL.quotedName(alias));
      }
      case Array.TYPE -> {
        return DslUtils.cast(field, getArrayType(), useSaferCasting).as(DSL.quotedName(alias));
      }
      case Union.TYPE -> {
        return castedField(field, ((Union) type).chooseType(), alias, useSaferCasting);
      }
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
    }
  }

  @NotNull
  @Override
  protected Field<?> castedField(@Nullable Field<?> field, @NotNull AirbyteProtocolType type, boolean useSaferCasting) {
    return DslUtils.cast(field, toDialectType(type), useSaferCasting);
  }

  @Nullable
  @Override
  protected Field<?> buildAirbyteMetaColumn(@NotNull LinkedHashMap<ColumnId, AirbyteType> columns) {
    final Field<?>[] dataFieldErrors = Stream.concat(Stream.concat(Stream.of(val("[")), columns
        .entrySet()
        .stream()
        .map(column -> toCastingErrorCaseStmt(column.getKey(), column.getValue()))), Stream.of(val("]")))
        .toArray(Field[]::new);

    final Field<?> finalTableChangesArray = DSL.replace(DSL.concat(dataFieldErrors), ", ]", "]");
    return DslUtils.jsonBuildObject(val(META_COLUMN_WARNINGS_KEY), finalTableChangesArray).as(COLUMN_NAME_AB_META);
  }

  private Field<Object> toCastingErrorCaseStmt(final ColumnId column, final AirbyteType type) {
    final DataType<?> dialectType = toDialectType(type);
    final Field<Object> extract = extractColumnAsString(column);
    return field(CASE_STATEMENT_SQL_TEMPLATE,
        canCast(extract, dialectType).isTrue(),
        val(""),
        val(String.format("Incorrect '%s' format for column '%s'(forced casting applied), ", dialectType.getTypeName(), column.getOriginalName())));
  }

  private Field<?> canCast(Field<?> field, DataType<?> dialectType) {
    final String database = config.get(JdbcUtils.DATABASE_KEY).asText();
    return function(name(database, "can_cast"), BOOLEAN, field, val(dialectType.getTypeName()));
  }

  @NotNull
  @Override
  protected Condition cdcDeletedAtNotNullCondition() {
    return field(name(COLUMN_NAME_AB_LOADED_AT)).isNotNull()
        .and(extractColumnAsString(getCdcDeletedAtColumn()).isNotNull());
  }

  @NotNull
  @Override
  protected Field<Integer> getRowNumber(@Nullable List<ColumnId> primaryKey, @NotNull Optional<ColumnId> cursorField) {
    final List<Field<?>> primaryKeyFields =
        primaryKey != null ? primaryKey.stream().map(columnId -> field(quotedName(columnId.getName()))).collect(Collectors.toList())
            : new ArrayList<>();
    final List<Field<?>> orderedFields = new ArrayList<>();
    cursorField.ifPresent(columnId -> orderedFields.add(field("{0} desc", field(quotedName(columnId.getName())))));
    orderedFields.add(field("{0} desc", quotedName(COLUMN_NAME_AB_EXTRACTED_AT)));
    return rowNumber().over().partitionBy(primaryKeyFields).orderBy(orderedFields).as(ROW_NUMBER_COLUMN_NAME);
  }

}
