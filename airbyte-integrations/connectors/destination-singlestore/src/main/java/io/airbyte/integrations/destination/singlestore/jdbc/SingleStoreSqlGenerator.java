/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore.jdbc;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.*;
import static io.airbyte.integrations.base.destination.typing_deduping.Sql.separately;
import static io.airbyte.integrations.base.destination.typing_deduping.Sql.transactionally;
import static org.jooq.impl.SQLDataType.VARCHAR;

import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.base.destination.typing_deduping.*;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.text.MessageFormat;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.jooq.DataType;
import org.jooq.SQLDialect;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreSqlGenerator implements SqlGenerator {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreSqlGenerator.class);
  private static final DataType<Object> JSON_TYPE = new DefaultDataType<>(SQLDialect.DEFAULT, Object.class, "json");
  private static final String META_COLUMN_WARNINGS_KEY = "warnings";
  public static final DateTimeFormatter TIMESTAMP_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSS").withZone(ZoneId.of("UTC"));
  public static final String CDC_DELETED_COLUMN_NAME = "_ab_cdc_deleted_at";
  public static final String QUOTE = "`";

  private final NamingConventionTransformer namingTransformer;

  public SingleStoreSqlGenerator(NamingConventionTransformer namingTransformer) {
    this.namingTransformer = namingTransformer;
  }

  @NotNull
  @Override
  public StreamId buildStreamId(final @NotNull String namespace, final @NotNull String name, final @NotNull String rawNamespaceOverride) {
    final String streamName = namingTransformer.getIdentifier(StreamId.concatenateRawTableName(namespace, name));
    return new StreamId(
        namingTransformer.getNamespace(namespace),
        namingTransformer.convertStreamName(name),
        namingTransformer.getNamespace(rawNamespaceOverride).toLowerCase(),
        streamName,
        namespace,
        name);
  }

  @NotNull
  @Override
  public ColumnId buildColumnId(@NotNull String name, @Nullable String suffix) {
    var nameWithSuffix = name + suffix;
    return new ColumnId(namingTransformer.getIdentifier(nameWithSuffix), name, namingTransformer.getIdentifier(nameWithSuffix));
  }

  @NotNull
  @Override
  public Sql createTable(@NotNull final StreamConfig stream, @NotNull final String suffix, final boolean force) {
    var columns = stream.getColumns().entrySet().stream().collect(Collectors.toMap(Map.Entry::getKey, e -> toDialectType(e.getValue())));
    var columnNameTypeMapping =
        Stream.of(getFinalTableMetaColumns(true), columns)
            .flatMap(it -> it.entrySet().stream())
            .map(it -> it.getKey().name(QUOTE) + " " + it.getValue()).collect(Collectors.joining(", \n"));
    var finalTableIdentifier = stream.getId().finalTableId(QUOTE, namingTransformer.applyDefaultCase(suffix));
    var dropTable = "";
    if (force) {
      dropTable = String.format("DROP TABLE IF EXISTS %s", finalTableIdentifier);
    }
    var createTable = String.format("CREATE TABLE %s (%s)", finalTableIdentifier, columnNameTypeMapping);
    return Sql.transactionally(dropTable, createTable);
  }

  public static DataType<?> toDialectType(AirbyteType type) {
    if (type instanceof AirbyteProtocolType) {
      return toDialectType((AirbyteProtocolType) type);
    }
    return switch (type.getTypeName()) {
      case Struct.TYPE, Array.TYPE -> JSON_TYPE;
      case Union.TYPE -> toDialectType(((Union) type).chooseType());
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + type.getTypeName());
    };
  }

  public static DataType<?> toDialectType(@NotNull AirbyteProtocolType airbyteProtocolType) {
    return switch (airbyteProtocolType) {
      case AirbyteProtocolType.STRING -> VARCHAR(21844);
      case AirbyteProtocolType.NUMBER -> SQLDataType.DECIMAL(38, 9);
      case AirbyteProtocolType.INTEGER -> SQLDataType.BIGINT;
      case AirbyteProtocolType.BOOLEAN -> SQLDataType.BOOLEAN;
      case AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE, AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE -> SQLDataType.TIMESTAMP(6);
      case AirbyteProtocolType.TIME_WITHOUT_TIMEZONE, AirbyteProtocolType.TIME_WITH_TIMEZONE -> SQLDataType.TIME(6);
      case AirbyteProtocolType.DATE -> SQLDataType.DATE;
      case AirbyteProtocolType.UNKNOWN -> SQLDataType.JSON;
    };
  }

  @NotNull
  @Override
  public Sql createSchema(@NotNull String database) {
    return Sql.of(String.format("CREATE DATABASE IF NOT EXISTS `%s`", database));
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
    var checkpointStmt = checkpointRawTable(rawSchema, rawTable, minRawTimestamp);
    if (destinationMode != DestinationSyncMode.APPEND_DEDUP) {
      var insertStmt = insertNewRecords(streamConfig, finalSuffix, minRawTimestamp, useExpensiveSaferCasting, false);
      if (Objects.equals(rawSchema, finalSchema)) {
        return transactionally(insertStmt, checkpointStmt);
      } else {
        LOGGER.warn("May cause inconsistent migration status. For safe integration use the same database for raw and final tables.");
        return separately(insertStmt, checkpointStmt);
      }
    }
    var insertStmtWithDedupe = insertNewRecords(streamConfig, finalSuffix, minRawTimestamp, useExpensiveSaferCasting, true);
    var deleteStmt =
        deleteFromFinalTable(
            finalSchema,
            finalTable,
            Objects.requireNonNull(streamConfig.getPrimaryKey()),
            streamConfig.getCursor());
    String deleteCdcDeletesStmt = "";
    if (streamConfig.getColumns().containsKey(getCdcDeletedAtColumn())) {
      deleteCdcDeletesStmt =
          MessageFormat.format("DELETE FROM {0} WHERE {1} IS NOT NULL", streamConfig.getId().finalTableId(QUOTE), quote(CDC_DELETED_COLUMN_NAME));
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

  private String insertNewRecords(
                                  StreamConfig stream,
                                  String finalSuffix,
                                  Optional<Instant> minRawTimestamp,
                                  boolean forceCast,
                                  boolean dedupe) {
    var finalColumnNames = Stream.concat(stream.getColumns().keySet().stream(), getFinalTableMetaColumns(false).keySet().stream())
        .map(e -> e.name(QUOTE)).collect(Collectors.joining(", \n"));
    return MessageFormat.format("INSERT INTO {0} ({1}, {2}) {3}",
        stream.getId().finalTableId(QUOTE, finalSuffix), finalColumnNames, quote(COLUMN_NAME_AB_META),
        selectTypedRecordsFromRawTable(stream, minRawTimestamp, finalColumnNames, forceCast, dedupe));
  }

  private String selectTypedRecordsFromRawTable(
                                                StreamConfig stream,
                                                Optional<Instant> minRawTimestamp,
                                                String finalColumnNames,
                                                Boolean safeCast,
                                                Boolean dedupe) {
    var projectionColumns = Stream.concat(
        stream.getColumns().entrySet().stream()
            .map(e -> String.format("%s as %s", cast(e.getKey().getOriginalName(), e.getValue(), safeCast), quote(e.getKey().getName()))),
        getFinalTableMetaColumns(false).keySet().stream().map(dataType -> quote(dataType.getName()))).collect(Collectors.joining(", \n"));
    var metaColumn = buildMetaColumn(stream.getColumns());
    String excludeCdcDeletedCondition = "";
    if (dedupe && stream.getColumns().containsKey(getCdcDeletedAtColumn())) {
      excludeCdcDeletedCondition =
          MessageFormat.format(" OR ({0} IS NOT NULL AND {1} IS NOT NULL)", quote(COLUMN_NAME_AB_LOADED_AT), jsonPath(CDC_DELETED_COLUMN_NAME));
    }
    String extractedAtCondition = "";
    if (minRawTimestamp.isPresent()) {
      extractedAtCondition =
          MessageFormat.format(" AND {0} > ''{1}''", COLUMN_NAME_AB_EXTRACTED_AT, TIMESTAMP_FORMATTER.format(minRawTimestamp.get()));
    }
    var rawTableSelectionCondition =
        MessageFormat.format(" ({0} is NULL{1}){2}",
            quote(COLUMN_NAME_AB_LOADED_AT), excludeCdcDeletedCondition, extractedAtCondition);
    var selectFromRawTable =
        MessageFormat.format("SELECT {0}, {1} FROM {2} WHERE {3}",
            projectionColumns, metaColumn, stream.getId().rawTableId(QUOTE), rawTableSelectionCondition);
    var selectCTENoDedupe =
        MessageFormat.format(" WITH {0} as ( {1} ) SELECT {2}, {3} FROM {0}", quote("intermediate_data"), selectFromRawTable, finalColumnNames,
            quote(COLUMN_NAME_AB_META));
    if (!dedupe) {
      return selectCTENoDedupe;
    }
    var cursorOrderBy = "";
    if (stream.getCursor().isPresent()) {
      cursorOrderBy = MessageFormat.format("{0} DESC,", stream.getCursor().get().name(QUOTE));
    }
    var commaSeperatedPks = stream.getPrimaryKey().stream().map(c -> c.name(QUOTE)).collect(Collectors.joining(", "));
    return MessageFormat.format("""
                                WITH intermediate_data as (
                                {0}
                                ), numbered_rows AS (
                                SELECT *, row_number() OVER (
                                PARTITION BY {1} ORDER BY {2} {3} DESC) as {4}
                                FROM {5})
                                SELECT
                                {6}, {7}
                                FROM {8}
                                WHERE {9} = 1""",
        selectFromRawTable, commaSeperatedPks, cursorOrderBy, quote(COLUMN_NAME_AB_EXTRACTED_AT), quote("row_number"),
        quote("intermediate_data"), finalColumnNames, quote(COLUMN_NAME_AB_META), quote("numbered_rows"), quote("row_number"));
  }

  private String buildMetaColumn(LinkedHashMap<ColumnId, AirbyteType> columns) {
    if (columns.isEmpty()) {
      return MessageFormat.format("JSON_BUILD_OBJECT(\n''{0}'',\n ''[]'')\n as {1}", META_COLUMN_WARNINGS_KEY, quote(COLUMN_NAME_AB_META));
    }
    return MessageFormat.format("JSON_BUILD_OBJECT(\n''{0}'',\n replace(concat(''['', {1}, '']''), '', ]'', '']''))\n as {2}",
        META_COLUMN_WARNINGS_KEY,
        columns.entrySet().stream().map(e -> canCastExpression(e.getKey().getOriginalName(), toDialectType(e.getValue()).getTypeName()))
            .collect(Collectors.joining(", \n")),
        quote(COLUMN_NAME_AB_META));
  }

  private String canCastExpression(String columnName, String type) {
    return MessageFormat.format(
        "cast(CASE WHEN {0}{1}(\n{2},\n''{3}''\n) = true THEN '''' ELSE ''Incorrect ''''{3}'''' format for column ''''{4}''''(forced casting applied), '' END  as char)",
        "", quote("can_cast"), jsonPath(columnName), type, escapeJsonDataColumnName(columnName));
  }

  private String quote(String value) {
    return MessageFormat.format("{0}{1}{0}", QUOTE, value);
  }

  private String cast(String columnName, AirbyteType columnType, Boolean force) {
    if (columnType.getTypeName().equals(AirbyteProtocolType.STRING.getTypeName())) {
      return jsonPath(columnName);
    }
    if (columnType.getTypeName().equals(AirbyteProtocolType.BOOLEAN.getTypeName())) {
      return MessageFormat.format("({0} = ''TRUE'')", jsonPath(columnName));
    }
    final String sql = force ? "({0} !:> {1})" : "({0} :> {1})";
    return MessageFormat.format(sql, jsonPath(columnName), toDialectType(columnType));
  }

  private String jsonPath(String originalColumnName) {
    return MessageFormat.format("json_extract_string({0}, ''{1}'')", COLUMN_NAME_DATA, escapeJsonDataColumnName(originalColumnName));
  }

  private String checkpointRawTable(String schemaName, String tableName, Optional<Instant> minRawTimestamp) {
    var table = MessageFormat.format("{0}.{1}", quote(schemaName), quote(tableName));
    String checkpointCondition = minRawTimestamp.map(instant -> MessageFormat.format("{0} IS NULL AND {1} > ''{2}''",
        quote(COLUMN_NAME_AB_LOADED_AT), quote(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT), TIMESTAMP_FORMATTER.format(instant)))
        .orElseGet(() -> MessageFormat.format("{0} IS NULL", quote(COLUMN_NAME_AB_LOADED_AT)));
    return MessageFormat.format("update {0} set {1} = current_timestamp() where {2}", table, quote(COLUMN_NAME_AB_LOADED_AT), checkpointCondition);
  }

  private String deleteFromFinalTable(
                                      String schemaName,
                                      String tableName,
                                      List<ColumnId> primaryKeys,
                                      Optional<ColumnId> cursor) {
    var table = MessageFormat.format("{0}.{1}", quote(schemaName), quote(tableName));
    var cursorOrderBy = "";
    if (cursor.isPresent()) {
      cursorOrderBy = MessageFormat.format("{0} DESC,", cursor.get().name(QUOTE));
    }
    var commaSeperatedPks = primaryKeys.stream().map(c -> c.name(QUOTE)).collect(Collectors.joining(", "));
    var selectStmt = MessageFormat.format(
        "SELECT {0} FROM (SELECT {0}, row_number() OVER (PARTITION BY {1} ORDER BY {2} {3} DESC) AS `row_number` FROM {4}) as `airbyte_ids` WHERE `row_number` <> 1",
        quote(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID), commaSeperatedPks, cursorOrderBy, quote(COLUMN_NAME_AB_EXTRACTED_AT), table);
    return MessageFormat.format("DELETE FROM {0} WHERE {1} IN ({2})", table, quote(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID), selectStmt);
  }

  private ColumnId getCdcDeletedAtColumn() {
    return buildColumnId(CDC_DELETED_COLUMN_NAME);
  }

  private LinkedHashMap<ColumnId, DataType<?>> getFinalTableMetaColumns(boolean includeMetaColumn) {
    var metaColumns = new LinkedHashMap<ColumnId, DataType<?>>();
    metaColumns.put(buildColumnId(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID), SQLDataType.VARCHAR(36).nullable(false));
    metaColumns.put(buildColumnId(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT), SQLDataType.TIMESTAMP(6).nullable(false));
    metaColumns.put(buildColumnId(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID), SQLDataType.BIGINT);
    if (includeMetaColumn) {
      metaColumns.put(buildColumnId(JavaBaseConstants.COLUMN_NAME_AB_META), SQLDataType.JSON.nullable(false));
    }
    return metaColumns;
  }

  @NotNull
  @Override
  public Sql overwriteFinalTable(@NotNull StreamId streamId, @NotNull String suffix) {
    return Sql.transactionally(String.format("DROP TABLE IF EXISTS %s", streamId.finalTableId(QUOTE)),
        String.format("ALTER TABLE %s RENAME TO %s", streamId.finalTableId(QUOTE, suffix), streamId.finalTableId(QUOTE)));
  }

  @NotNull
  @Override
  public Sql migrateFromV1toV2(@NotNull StreamId streamId, @NotNull String s, @NotNull String s1) {
    throw new UnsupportedOperationException("This method is not allowed");
  }

  @NotNull
  @Override
  public Sql clearLoadedAt(@NotNull StreamId streamId) {
    return Sql.of(String.format("UPDATE %s SET %s = NULL", streamId.rawTableId(QUOTE), JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT));
  }

  public Sql createRawTable(@NotNull StreamId streamId) {
    var sql = String.format("""
                            CREATE TABLE IF NOT EXISTS %s.%s (
                            %s VARCHAR(256),
                            %s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6),
                            %s TIMESTAMP(6) DEFAULT NULL,
                            %s JSON,
                            %s JSON,
                            %s BIGINT,
                            SORT KEY (%s));""", streamId.getRawNamespace(), streamId.getRawName(), JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_AB_META, JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID,
        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT);
    return Sql.of(sql);
  }

  private String escapeJsonDataColumnName(String columnName) {
    return columnName
        .replace("\\", "\\\\")
        .replace("\"", "\\\"")
        .replace("'", "\\'");
  }

  public Sql truncateRawTable(StreamId streamId) {
    return Sql.of(
        String.format("TRUNCATE TABLE %s.%s", streamId.getRawNamespace(), streamId.getRawName()));
  }

}
