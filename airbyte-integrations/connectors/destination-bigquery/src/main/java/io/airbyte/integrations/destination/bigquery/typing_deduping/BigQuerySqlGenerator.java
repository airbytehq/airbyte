/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static java.util.stream.Collectors.joining;

import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableDefinition;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.UnsupportedOneOf;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteTypeUtils;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.apache.commons.text.StringSubstitutor;

public class BigQuerySqlGenerator implements SqlGenerator<TableDefinition> {

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

    // Column names aren't allowed to start with certain strings. Prepend an underscore if this happens.
    final List<String> invalidColumnPrefixes = List.of(
        "_table_",
        "_file_",
        "_partition_",
        "_row_timestamp_",
        "__root__",
        "_colidentifier_"
    );
    String canonicalized = name.toLowerCase();
    // Bigquery columns are case insensitive, so do all our validation on the lowercased name
    if (invalidColumnPrefixes.stream().anyMatch(prefix -> name.toLowerCase().startsWith(prefix))) {
      quotedName = "_" + quotedName;
      canonicalized = "_" + canonicalized;
    }

    // TODO this is probably wrong
    return new ColumnId(nameTransformer.getIdentifier(quotedName), name, canonicalized);
  }

  public StandardSQLTypeName toDialectType(final AirbyteType type) {
    // switch pattern-matching is still in preview at language level 17 :(
    if (type instanceof final AirbyteProtocolType p) {
      return toDialectType(p);
    } else if (type instanceof Struct) {
      return StandardSQLTypeName.JSON;
    } else if (type instanceof Array) {
      return StandardSQLTypeName.JSON;
    } else if (type instanceof UnsupportedOneOf) {
      return StandardSQLTypeName.JSON;
    } else if (type instanceof final OneOf o) {
      final AirbyteType typeWithPrecedence = AirbyteTypeUtils.chooseOneOfType(o);
      final StandardSQLTypeName dialectType;
      if ((typeWithPrecedence instanceof Struct) || (typeWithPrecedence instanceof Array)) {
        dialectType = StandardSQLTypeName.JSON;
      } else {
        dialectType = toDialectType((AirbyteProtocolType) typeWithPrecedence);
      }
      return dialectType;
    }

    // Literally impossible; AirbyteType is a sealed interface.
    throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
  }

  private String extractAndCast(final ColumnId column, final AirbyteType airbyteType) {
    if (airbyteType instanceof OneOf o) {
      // This is guaranteed to not be a OneOf, so we won't recurse infinitely
      final AirbyteType chosenType = AirbyteTypeUtils.chooseOneOfType(o);
      return extractAndCast(column, chosenType);
    } else if (airbyteType instanceof Struct) {
      // We need to validate that the struct is actually a struct.
      // Note that struct columns are actually nullable in two ways. For a column `foo`:
      // {foo: null} and {} are both valid, and are both written to the final table as a SQL NULL (_not_ a
      // JSON null).
      // JSON_QUERY(JSON'{}', '$.foo') returns a SQL null.
      // JSON_QUERY(JSON'{"foo": null}', '$.foo') returns a JSON null.
      return new StringSubstitutor(Map.of("column_name", column.originalName())).replace(
          """
          CASE
            WHEN JSON_QUERY(`_airbyte_data`, '$.${column_name}') IS NULL
              OR JSON_TYPE(JSON_QUERY(`_airbyte_data`, '$.${column_name}')) != 'object'
              THEN NULL
            ELSE JSON_QUERY(`_airbyte_data`, '$.${column_name}')
          END
          """);
    } else if (airbyteType instanceof Array) {
      // Much like the Struct case above, arrays need special handling.
      return new StringSubstitutor(Map.of("column_name", column.originalName())).replace(
          """
          CASE
            WHEN JSON_QUERY(`_airbyte_data`, '$.${column_name}') IS NULL
              OR JSON_TYPE(JSON_QUERY(`_airbyte_data`, '$.${column_name}')) != 'array'
              THEN NULL
            ELSE JSON_QUERY(`_airbyte_data`, '$.${column_name}')
          END
          """);
    } else if (airbyteType instanceof UnsupportedOneOf || airbyteType == AirbyteProtocolType.UNKNOWN) {
      // JSON_VALUE converts JSON types to native SQL types (int64, string, etc.)
      // We use JSON_QUERY rather than JSON_VALUE so that we can extract a JSON-typed value.
      // This is to avoid needing to convert the raw SQL type back into JSON.
      return "JSON_QUERY(`_airbyte_data`, '$." + column.originalName() + "')";
    } else {
      final StandardSQLTypeName dialectType = toDialectType(airbyteType);
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
  public String createTable(final StreamConfig stream, final String suffix) {
    final String columnDeclarations = stream.columns().entrySet().stream()
        .map(column -> column.getKey().name(QUOTE) + " " + toDialectType(column.getValue()).name())
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
        "cluster_config", clusterConfig)).replace(
            """
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
  public String alterTable(final StreamConfig stream,
                           final TableDefinition existingTable) {
    if (existingTable instanceof final StandardTableDefinition s) {
      // TODO check if clustering/partitioning config is different from what we want, do something to
      // handle it
      // iirc this will depend on the stream (destination?) sync mode + cursor + pk name
      if (s.getClustering() != null) {

      }
    } else {
      // TODO idk
    }
    /*
     * TODO maybe we do something like this? CREATE OR REPLACE TABLE ${final_table_id} AS ( SELECT
     * _airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta, -- cast columns when needed CAST(col1 AS
     * new_type) AS col1, -- some columns will not change at all col2, -- new columns default to null
     * NULL as col3 ... FROM ${final_table_id} )
     *
     * This has a few advantages: * bypasses the whole "you can only alter certain column types" problem
     * * preserves column ordering
     *
     * But it does mean that we have to rewrite the entire table, which really sucks. But maybe that's
     * fine, since it only happens on schema change? And it's presumably no worse than a soft reset.
     */
    return "";
  }

  @Override
  public String updateTable(final String finalSuffix, final StreamConfig stream) {
    String validatePrimaryKeys = "";
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      validatePrimaryKeys = validatePrimaryKeys(stream.id(), stream.primaryKey(), stream.columns());
    }
    final String insertNewRecords = insertNewRecords(stream.id(), finalSuffix, stream.columns(), stream.destinationSyncMode());
    String dedupFinalTable = "";
    String cdcDeletes = "";
    String dedupRawTable = "";
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      dedupRawTable = dedupRawTable(stream.id(), finalSuffix);
      // If we're in dedup mode, then we must have a cursor
      dedupFinalTable = dedupFinalTable(stream.id(), finalSuffix, stream.primaryKey(), stream.cursor().get());
      cdcDeletes = cdcDeletes(stream, finalSuffix, stream.columns());
    }
    final String commitRawTable = commitRawTable(stream.id());

    return new StringSubstitutor(Map.of(
        "validate_primary_keys", validatePrimaryKeys,
        "insert_new_records", insertNewRecords,
        "dedup_final_table", dedupFinalTable,
        "cdc_deletes", cdcDeletes,
        "dedupe_raw_table", dedupRawTable,
        "commit_raw_table", commitRawTable)).replace(
            """
            DECLARE missing_pk_count INT64;

            BEGIN TRANSACTION;

            ${validate_primary_keys}

            ${insert_new_records}

            ${dedup_final_table}

            ${dedupe_raw_table}

            ${cdc_deletes}

            ${commit_raw_table}

            COMMIT TRANSACTION;
            """);
  }

  @VisibleForTesting
  String validatePrimaryKeys(final StreamId id,
                             final List<ColumnId> primaryKeys,
                             final LinkedHashMap<ColumnId, AirbyteType> streamColumns) {
    final String pkNullChecks = primaryKeys.stream().map(
        pk -> {
          final String jsonExtract = extractAndCast(pk, streamColumns.get(pk));
          return "AND " + jsonExtract + " IS NULL";
        }).collect(joining("\n"));

    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE),
        "pk_null_checks", pkNullChecks)).replace(
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
            END IF
            ;""");
  }

  @VisibleForTesting
  String insertNewRecords(final StreamId id, final String finalSuffix, final LinkedHashMap<ColumnId, AirbyteType> streamColumns, DestinationSyncMode destinationSyncMode) {
    final String columnCasts = streamColumns.entrySet().stream().map(
        col -> extractAndCast(col.getKey(), col.getValue()) + " as " + col.getKey().name(QUOTE) + ",")
        .collect(joining("\n"));
    final String columnErrors = streamColumns.entrySet().stream().map(
        col -> new StringSubstitutor(Map.of(
            "raw_col_name", col.getKey().originalName(),
            "col_type", toDialectType(col.getValue()).name(),
            "json_extract", extractAndCast(col.getKey(), col.getValue()))).replace(
                """
                CASE
                  WHEN (JSON_QUERY(`_airbyte_data`, '$.${raw_col_name}') IS NOT NULL)
                    AND (JSON_TYPE(JSON_QUERY(`_airbyte_data`, '$.${raw_col_name}')) != 'null')
                    AND (${json_extract} IS NULL)
                    THEN ["Problem with `${raw_col_name}`"]
                  ELSE []
                END"""))
        .collect(joining(",\n"));
    final String columnList = streamColumns.keySet().stream().map(quotedColumnId -> quotedColumnId.name(QUOTE) + ",").collect(joining("\n"));
    final String deletionClause;
    if (destinationSyncMode == DestinationSyncMode.APPEND_DEDUP && streamColumns.keySet().stream().anyMatch(col -> "_ab_cdc_deleted_at".equals(col.originalName()))) {
      deletionClause = """
          AND (
            JSON_QUERY(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NULL
            OR JSON_TYPE(JSON_QUERY(`_airbyte_data`, '$._ab_cdc_deleted_at')) = 'null'
          )
          """;
    } else {
      deletionClause = "";
    }

    String cdcConditionalOrIncludeStatement = "";
    if (streamColumns.containsKey(CDC_DELETED_AT_COLUMN)){
      cdcConditionalOrIncludeStatement = """
      OR (
        _airbyte_loaded_at IS NOT NULL
        AND JSON_VALUE(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NOT NULL
      )
      """;
    }

    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE),
        "final_table_id", id.finalTableId(finalSuffix, QUOTE),
        "column_casts", columnCasts,
        "column_errors", columnErrors,
        "cdcConditionalOrIncludeStatement", cdcConditionalOrIncludeStatement,
        "column_list", columnList)).replace(
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
                    ${cdcConditionalOrIncludeStatement}
                )
                SELECT
                ${column_list}
                  to_json(struct(_airbyte_cast_errors AS errors)) AS _airbyte_meta,
                  _airbyte_raw_id,
                  _airbyte_extracted_at
                FROM intermediate_data;""");
  }

  @VisibleForTesting
  String dedupFinalTable(final StreamId id,
                         final String finalSuffix,
                         final List<ColumnId> primaryKey,
                         final ColumnId cursor) {
    final String pkList = primaryKey.stream().map(columnId -> columnId.name(QUOTE)).collect(joining(","));

    return new StringSubstitutor(Map.of(
        "final_table_id", id.finalTableId(finalSuffix, QUOTE),
        "pk_list", pkList,
        "cursor_name", cursor.name(QUOTE))
        ).replace(
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
            ;""");
  }

  @VisibleForTesting
  String cdcDeletes(final StreamConfig stream,
      final String finalSuffix,
      final LinkedHashMap<ColumnId, AirbyteType> streamColumns) {

    if (stream.destinationSyncMode() != DestinationSyncMode.APPEND_DEDUP){
      return "";
    }

    if (!streamColumns.containsKey(CDC_DELETED_AT_COLUMN)){
      return "";
    }

    final String pkList = stream.primaryKey().stream().map(columnId -> columnId.name(QUOTE)).collect(joining(","));
    String pkCasts = stream.primaryKey().stream().map(pk -> extractAndCast(pk, streamColumns.get(pk))).collect(joining(",\n"));

    // we want to grab IDs for deletion from the raw table (not the final table itself) to hand out-of-order record insertions after the delete has been registered
    return new StringSubstitutor(Map.of(
        "final_table_id", stream.id().finalTableId(finalSuffix, QUOTE),
        "raw_table_id", stream.id().rawTableId(QUOTE),
        "pk_list", pkList,
        "pk_extracts", pkCasts,
        "quoted_cdc_delete_column", QUOTE + "_ab_cdc_deleted_at" + QUOTE)
    ).replace(
        """
        DELETE FROM ${final_table_id}
        WHERE
          (${pk_list}) IN (
            SELECT (
                ${pk_extracts}
              )
            FROM  ${raw_table_id}
            WHERE
              JSON_VALUE(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NOT NULL
          )
        ;"""
    );
  }

  @VisibleForTesting
  String dedupRawTable(final StreamId id, final String finalSuffix) {
    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE),
        "final_table_id", id.finalTableId(finalSuffix, QUOTE))).replace(
            // Note that this leaves _all_ deletion records in the raw table. We _could_ clear them out, but it
            // would be painful,
            // and it only matters in a few edge cases.
            """
            DELETE FROM
              ${raw_table_id}
            WHERE
              `_airbyte_raw_id` NOT IN (
                SELECT `_airbyte_raw_id` FROM ${final_table_id}
              )
            ;""");
  }

  @VisibleForTesting
  String commitRawTable(final StreamId id) {
    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE))).replace(
            """
            UPDATE ${raw_table_id}
            SET `_airbyte_loaded_at` = CURRENT_TIMESTAMP()
            WHERE `_airbyte_loaded_at` IS NULL
            ;""");
  }

  @Override
  public Optional<String> overwriteFinalTable(final String finalSuffix, final StreamConfig stream) {
    if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE && finalSuffix.length() > 0) {
      return Optional.of(new StringSubstitutor(Map.of(
          "final_table_id", stream.id().finalTableId(QUOTE),
          "tmp_final_table", stream.id().finalTableId(finalSuffix, QUOTE),
          "real_final_table", stream.id().finalName(QUOTE))).replace(
              """
              DROP TABLE IF EXISTS ${final_table_id};
              ALTER TABLE ${tmp_final_table} RENAME TO ${real_final_table};
              """));
    } else {
      return Optional.empty();
    }
  }

}
