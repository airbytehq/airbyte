package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static java.util.stream.Collectors.joining;

import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableDefinition;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Struct;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.UnsupportedOneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.ParsedType;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.StreamConfig;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.apache.commons.text.StringSubstitutor;

public class BigQuerySqlGenerator implements SqlGenerator<TableDefinition, StandardSQLTypeName> {

  public static final String QUOTE = "`";
  private static final BigQuerySQLNameTransformer nameTransformer = new BigQuerySQLNameTransformer();

  private final ColumnId CDC_DELETED_AT_COLUMN = buildColumnId("_ab_cdc_deleted_at");

  @Override
  public StreamId buildStreamId(final String namespace, final String name, final String rawNamespaceOverride) {
    return new StreamId(
        // TODO is this correct?
        nameTransformer.getNamespace(namespace),
        nameTransformer.convertStreamName(name),
        nameTransformer.getNamespace(rawNamespaceOverride),
        nameTransformer.convertStreamName(namespace + "_" + name),
        namespace,
        name);
  }

  @Override
  public ColumnId buildColumnId(final String name) {
    String quotedName = name;

    // Bigquery columns are case insensitive, so do all our validation on the lowercased name
    String canonicalized = name.toLowerCase();

    // Column names aren't allowed to start with certain strings. Prepend an underscore if this happens.
    if (canonicalized.startsWith("_table_")
        || canonicalized.startsWith("_file_")
        || canonicalized.startsWith("_partition_")
        || canonicalized.startsWith("_row_timestamp_")
        // yes, there are two underscores here. That's intentional.
        || canonicalized.startsWith("__root__")
        || canonicalized.startsWith("_colidentifier_")) {
      quotedName = "_" + quotedName;
      canonicalized = "_" + canonicalized;
    }

    // TODO this is probably wrong
    return new ColumnId(nameTransformer.getIdentifier(quotedName), name, canonicalized);
  }

  @Override
  public ParsedType<StandardSQLTypeName> toDialectType(final AirbyteType type) {
    // switch pattern-matching is still in preview at language level 17 :(
    if (type instanceof final AirbyteProtocolType p) {
      return new ParsedType<>(toDialectType(p), type);
    } else if (type instanceof Struct) {
      return new ParsedType<>(StandardSQLTypeName.JSON, type);
    } else if (type instanceof Array) {
      return new ParsedType<>(StandardSQLTypeName.JSON, type);
    } else if (type instanceof UnsupportedOneOf) {
      return new ParsedType<>(StandardSQLTypeName.JSON, type);
    } else if (type instanceof final OneOf o) {
      final AirbyteType typeWithPrecedence = AirbyteTypeUtils.chooseOneOfType(o);
      final StandardSQLTypeName dialectType;
      if ((typeWithPrecedence instanceof Struct) || (typeWithPrecedence instanceof Array)) {
        dialectType = StandardSQLTypeName.JSON;
      } else {
        dialectType = toDialectType((AirbyteProtocolType) typeWithPrecedence);
      }
      return new ParsedType<>(dialectType, typeWithPrecedence);
    }

    // Literally impossible; AirbyteType is a sealed interface.
    throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
  }

  private String extractAndCast(final ColumnId column, final AirbyteType airbyteType, final StandardSQLTypeName dialectType) {
    if (airbyteType instanceof OneOf o) {
      // This is guaranteed to not be a OneOf, so we won't recurse infinitely
      final AirbyteType chosenType = AirbyteTypeUtils.chooseOneOfType(o);
      return extractAndCast(column, chosenType, dialectType);
    } else if (airbyteType instanceof Struct || airbyteType instanceof Array || airbyteType instanceof UnsupportedOneOf || airbyteType == AirbyteProtocolType.UNKNOWN) {
      return "JSON_QUERY(`_airbyte_data`, '$." + column.originalName() + "')";
    } else {
      return "SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$." + column.originalName() + "') as " + dialectType.name() + ")";
    }
  }

  public StandardSQLTypeName toDialectType(final AirbyteProtocolType airbyteProtocolType) {
    return switch (airbyteProtocolType) {
      // TODO doublecheck these
      case STRING -> StandardSQLTypeName.STRING;
      case NUMBER -> StandardSQLTypeName.NUMERIC;
      case INTEGER -> StandardSQLTypeName.INT64;
      case BOOLEAN -> StandardSQLTypeName.BOOL;
      case TIMESTAMP_WITH_TIMEZONE -> StandardSQLTypeName.TIMESTAMP;
      case TIMESTAMP_WITHOUT_TIMEZONE -> StandardSQLTypeName.DATETIME;
      case TIME_WITH_TIMEZONE -> StandardSQLTypeName.STRING;
      case TIME_WITHOUT_TIMEZONE -> StandardSQLTypeName.TIME;
      case DATE -> StandardSQLTypeName.DATE;
      case UNKNOWN -> StandardSQLTypeName.JSON;
    };
  }

  @Override
  public String createTable(final StreamConfig<StandardSQLTypeName> stream, final String suffix) {
    final String columnDeclarations = stream.columns().entrySet().stream()
        .map(column -> column.getKey().name(QUOTE) + " " + column.getValue().dialectType().name())
        .collect(joining(",\n"));
    final String clusterConfig;
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      // We're doing deduping, therefore we have a primary key.
      // Cluster on all the PK columns, and also extracted_at.
      clusterConfig = stream.primaryKey().stream().map(columnId -> columnId.name(QUOTE)).collect(joining(",")) + ", _airbyte_extracted_at";
    } else {
      // Otherwise just cluser on extracted_at.
      clusterConfig = "_airbyte_extracted_at";
    }

    return new StringSubstitutor(Map.of(
        "final_namespace", stream.id().finalNamespace(QUOTE),
        "final_table_id", stream.id().finalTableId(suffix, QUOTE),
        "column_declarations", columnDeclarations,
        "cluster_config", clusterConfig
    )).replace("""
        CREATE SCHEMA IF NOT EXISTS ${final_namespace};
        
        CREATE TABLE ${final_table_id} (
        _airbyte_raw_id STRING NOT NULL,
        _airbyte_extracted_at TIMESTAMP NOT NULL,
        _airbyte_meta JSON NOT NULL,
        ${column_declarations}
        )
        PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
        CLUSTER BY ${cluster_config}
        """);
  }

  @Override
  public String alterTable(final StreamConfig<StandardSQLTypeName> stream,
                           final TableDefinition existingTable) {
    if (existingTable instanceof final StandardTableDefinition s) {
      // TODO check if clustering/partitioning config is different from what we want, do something to handle it
      // iirc this will depend on the stream (destination?) sync mode + cursor + pk name
      if (s.getClustering() != null) {

      }
    } else {
      // TODO idk
    }
    /*
     * TODO maybe we do something like this?
     *  CREATE OR REPLACE TABLE ${final_table_id} AS (
     *    SELECT
     *      _airbyte_raw_id,
     *      _airbyte_extracted_at,
     *      _airbyte_meta,
     *      -- cast columns when needed
     *      CAST(col1 AS new_type) AS col1,
     *      -- some columns will not change at all
     *      col2,
     *      -- new columns default to null
     *      NULL as col3
     *      ...
     *    FROM ${final_table_id}
     *  )
     *
     * This has a few advantages:
     * * bypasses the whole "you can only alter certain column types" problem
     * * preserves column ordering
     *
     * But it does mean that we have to rewrite the entire table, which really sucks. But maybe that's fine, since it only happens on schema change?
     * And it's presumably no worse than a soft reset.
     */
    return "";
  }

  @Override
  public String updateTable(final String finalSuffix, final StreamConfig<StandardSQLTypeName> stream) {
    String validatePrimaryKeys = "";
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      validatePrimaryKeys = validatePrimaryKeys(stream.id(), stream.primaryKey(), stream.columns());
    }
    final String insertNewRecords = insertNewRecords(stream.id(), finalSuffix, stream.columns());
    String dedupFinalTable = "";
    String dedupRawTable = "";
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      dedupRawTable = dedupRawTable(stream.id(), finalSuffix, stream.columns());
      // If we're in dedup mode, then we must have a cursor
      dedupFinalTable = dedupFinalTable(stream.id(), finalSuffix, stream.primaryKey(), stream.cursor().get(), stream.columns());
    }
    final String commitRawTable = commitRawTable(stream.id());

    return new StringSubstitutor(Map.of(
        "validate_primary_keys", validatePrimaryKeys,
        "insert_new_records", insertNewRecords,
        "dedup_final_table", dedupFinalTable,
        "dedupe_raw_table", dedupRawTable,
        "commit_raw_table", commitRawTable
    )).replace(
        """
            DECLARE missing_pk_count INT64;
                        
            BEGIN TRANSACTION;
            ${validate_primary_keys}
                      
            ${insert_new_records}
                      
            ${dedup_final_table}
                      
            ${dedupe_raw_table}
                      
            ${commit_raw_table}
                      
            COMMIT TRANSACTION;
            """
    );
  }

  @VisibleForTesting
  String validatePrimaryKeys(final StreamId id, final List<ColumnId> primaryKeys, final LinkedHashMap<ColumnId, ParsedType<StandardSQLTypeName>> streamColumns) {
    final String pkNullChecks = primaryKeys.stream().map(
        pk -> {
          final String jsonExtract = extractAndCast(pk, streamColumns.get(pk).airbyteType(), streamColumns.get(pk).dialectType());
          return "AND " + jsonExtract + " IS NULL";
        }
    ).collect(joining("\n"));

    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE),
        "pk_null_checks", pkNullChecks
    )).replace(
        """
              SET missing_pk_count = (
                SELECT COUNT(1)
                FROM ${raw_table_id}
                WHERE
                  `_airbyte_loaded_at` IS NULL
                  ${pk_null_checks}
                );
                      
              IF missing_pk_count > 0 THEN
                RAISE USING message = FORMAT("Raw table has %s rows missing a primary key", CAST(missing_pk_count AS STRING));
              END IF;""");
  }

  @VisibleForTesting
  String insertNewRecords(final StreamId id, final String finalSuffix, final LinkedHashMap<ColumnId, ParsedType<StandardSQLTypeName>> streamColumns) {
    final String columnCasts = streamColumns.entrySet().stream().map(
        col -> extractAndCast(col.getKey(), col.getValue().airbyteType(), col.getValue().dialectType()) + " as " + col.getKey().name(QUOTE) + ","
    ).collect(joining("\n"));
    final String columnErrors = streamColumns.entrySet().stream().map(
        col -> new StringSubstitutor(Map.of(
            "raw_col_name", col.getKey().originalName(),
            "col_type", col.getValue().dialectType().name(),
            "json_extract", extractAndCast(col.getKey(), col.getValue().airbyteType(), col.getValue().dialectType())
        )).replace(
            // TODO check that json_extract is an object/array
            """
                CASE
                  WHEN (JSON_VALUE(`_airbyte_data`, '$.${raw_col_name}') IS NOT NULL) AND (${json_extract} IS NULL) THEN ["Problem with `${raw_col_name}`"]
                  ELSE []
                END"""
        )
    ).collect(joining(",\n"));
    final String columnList = streamColumns.keySet().stream().map(quotedColumnId -> quotedColumnId.name(QUOTE) + ",").collect(joining("\n"));

    // Note that we intentionally excluded deleted records from this insert. See dedupRawRecords for an explanation of how CDC deletes work.
    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE),
        "final_table_id", id.finalTableId(finalSuffix, QUOTE),
        "column_casts", columnCasts,
        "column_errors", columnErrors,
        "column_list", columnList
    )).replace(
        """
            INSERT INTO ${final_table_id}
            (
            ${column_list}
              _airbyte_meta,
              _airbyte_raw_id,
              _airbyte_extracted_at
            )
            WITH intermediate_data AS (
              SELECT
            ${column_casts}
              array_concat(
            ${column_errors}
              ) as _airbyte_cast_errors,
              _airbyte_raw_id,
              _airbyte_extracted_at
              FROM ${raw_table_id}
              WHERE
                _airbyte_loaded_at IS NULL
                AND JSON_EXTRACT(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NULL
            )
            SELECT
            ${column_list}
              CASE
                WHEN array_length(_airbyte_cast_errors) = 0 THEN JSON'{}'
                ELSE to_json(struct(_airbyte_cast_errors AS errors))
              END AS _airbyte_meta,
              _airbyte_raw_id,
              _airbyte_extracted_at
            FROM intermediate_data;"""
    );
  }

  @VisibleForTesting
  String dedupFinalTable(final StreamId id, final String finalSuffix, final List<ColumnId> primaryKey, final ColumnId cursor, final LinkedHashMap<ColumnId, ParsedType<StandardSQLTypeName>> streamColumns) {
    final String pkList = primaryKey.stream().map(columnId -> columnId.name(QUOTE)).collect(joining(","));
    final String pkCastList = streamColumns.entrySet().stream()
        .filter(e -> primaryKey.contains(e.getKey()))
        .map(e -> extractAndCast(e.getKey(), e.getValue().airbyteType(), e.getValue().dialectType()))
        .collect(joining(",\n "));
    final String cursorCast = extractAndCast(cursor, streamColumns.get(cursor).airbyteType(), streamColumns.get(cursor).dialectType());

    // See dedupRawTable for an explanation of why we delete records using the raw data rather than the final table's _ab_cdc_deleted_at column.
    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE),
        "final_table_id", id.finalTableId(finalSuffix, QUOTE),
        "pk_list", pkList,
        "pk_cast_list", pkCastList,
        "cursor_name", cursor.name(QUOTE),
        "cursor_cast", cursorCast
    )).replace(
        """
            DELETE FROM ${final_table_id}
            WHERE
              `_airbyte_raw_id` IN (
                SELECT `_airbyte_raw_id` FROM (
                  SELECT `_airbyte_raw_id`, row_number() OVER (
                    PARTITION BY ${pk_list} ORDER BY ${cursor_name} DESC, `_airbyte_extracted_at` DESC
                  ) as row_number FROM ${final_table_id}
                )
                WHERE row_number != 1
              )
              OR (
                ${pk_list} IN (
                  SELECT (
            ${pk_cast_list}
                  )
                  FROM ${raw_table_id}
                  WHERE
                    JSON_VALUE(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NOT NULL
                    AND ${cursor_name} < ${cursor_cast}
                )
              );"""
    );
  }

  @VisibleForTesting
  String dedupRawTable(final StreamId id, final String finalSuffix, LinkedHashMap<ColumnId, ParsedType<StandardSQLTypeName>> streamColumns) {
    /*
     * Note that we need to keep the deletion raw records because of how async syncs work. Consider this sequence of source events:
     * 1. Insert record id=1
     * 2. Update record id=1
     * 3. Delete record id=1
     *
     * It's possible for the destination to receive them out of order, e.g.:
     * 1. Insert
     * 2. Delete
     * 3. Update
     *
     * We can generally resolve this using the cursor column (e.g. multiple updates in the wrong order). However, deletions are special because we
     * propagate them as hard deletes to the final table. As a result, we need to keep the deletion in the raw table, so that a late-arriving update
     * doesn't incorrectly reinsert the final record.
     */
    String cdcDeletedAtClause;
    if (streamColumns.containsKey(CDC_DELETED_AT_COLUMN)) {
      cdcDeletedAtClause = "AND JSON_VALUE(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NULL";
    } else {
      cdcDeletedAtClause = "";
    }

    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE),
        "final_table_id", id.finalTableId(finalSuffix, QUOTE),
        "cdc_deleted_at_clause", cdcDeletedAtClause
    )).replace(
        // Note that this leaves _all_ deletion records in the raw table. We _could_ clear them out, but it would be painful,
        // and it only matters in a few edge cases.
        """
              DELETE FROM
                ${raw_table_id}
              WHERE
                `_airbyte_raw_id` NOT IN (
                  SELECT `_airbyte_raw_id` FROM ${final_table_id}
                )
                ${cdc_deleted_at_clause}
              ;"""
    );
  }

  @VisibleForTesting
  String commitRawTable(final StreamId id) {
    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE)
    )).replace(
        """
              UPDATE ${raw_table_id}
              SET `_airbyte_loaded_at` = CURRENT_TIMESTAMP()
              WHERE `_airbyte_loaded_at` IS NULL
              ;"""
    );
  }

  @Override
  public Optional<String> overwriteFinalTable(final String finalSuffix, final StreamConfig<StandardSQLTypeName> stream) {
    if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE && finalSuffix.length() > 0) {
      return Optional.of(new StringSubstitutor(Map.of(
          "final_table_id", stream.id().finalTableId(QUOTE),
          "tmp_final_table", stream.id().finalTableId(finalSuffix, QUOTE),
          "real_final_table", stream.id().finalName(QUOTE)
      )).replace("""
          DROP TABLE IF EXISTS ${final_table_id};
          ALTER TABLE ${tmp_final_table} RENAME TO ${real_final_table};
          """));
    } else {
      return Optional.empty();
    }
  }
}
