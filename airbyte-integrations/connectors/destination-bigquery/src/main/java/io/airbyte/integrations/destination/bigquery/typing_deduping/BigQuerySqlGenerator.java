/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static io.airbyte.integrations.base.destination.typing_deduping.Sql.separately;
import static io.airbyte.integrations.base.destination.typing_deduping.Sql.transactionally;
import static io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.SOFT_RESET_SUFFIX;
import static java.util.stream.Collectors.joining;

import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.common.annotations.VisibleForTesting;
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
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Stream;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.text.StringSubstitutor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQuerySqlGenerator implements SqlGenerator {

  public static final String QUOTE = "`";
  private static final BigQuerySQLNameTransformer nameTransformer = new BigQuerySQLNameTransformer();

  private final ColumnId CDC_DELETED_AT_COLUMN = buildColumnId("_ab_cdc_deleted_at");

  private final Logger LOGGER = LoggerFactory.getLogger(BigQuerySqlGenerator.class);

  private final String projectId;
  private final String datasetLocation;

  /**
   * @param projectId
   * @param datasetLocation This is technically redundant with {@link BigQueryDestinationHandler}
   *        setting the query execution location, but let's be explicit since this is typically a
   *        compliance requirement.
   */
  public BigQuerySqlGenerator(final String projectId, final String datasetLocation) {
    this.projectId = projectId;
    this.datasetLocation = datasetLocation;
  }

  @Override
  public StreamId buildStreamId(final String namespace, final String name, final String rawNamespaceOverride) {
    return new StreamId(
        nameTransformer.getNamespace(namespace),
        nameTransformer.convertStreamName(name),
        nameTransformer.getNamespace(rawNamespaceOverride),
        nameTransformer.convertStreamName(StreamId.concatenateRawTableName(namespace, name)),
        namespace,
        name);
  }

  @Override
  public ColumnId buildColumnId(final String name, final String suffix) {
    final String nameWithSuffix = name + suffix;
    return new ColumnId(
        nameTransformer.getIdentifier(nameWithSuffix),
        name,
        // Bigquery columns are case-insensitive, so do all our validation on the lowercased name
        nameTransformer.getIdentifier(nameWithSuffix.toLowerCase()));
  }

  public static StandardSQLTypeName toDialectType(final AirbyteType type) {
    // switch pattern-matching is still in preview at language level 17 :(
    if (type instanceof final AirbyteProtocolType p) {
      return toDialectType(p);
    } else if (type instanceof Struct) {
      return StandardSQLTypeName.JSON;
    } else if (type instanceof Array) {
      return StandardSQLTypeName.JSON;
    } else if (type instanceof UnsupportedOneOf) {
      return StandardSQLTypeName.JSON;
    } else if (type instanceof final Union u) {
      final AirbyteType typeWithPrecedence = u.chooseType();
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

  private String extractAndCast(final ColumnId column, final AirbyteType airbyteType, final boolean forceSafeCast) {
    if (airbyteType instanceof final Union u) {
      // This is guaranteed to not be a Union, so we won't recurse infinitely
      final AirbyteType chosenType = u.chooseType();
      return extractAndCast(column, chosenType, forceSafeCast);
    }

    if (airbyteType instanceof Struct) {
      // We need to validate that the struct is actually a struct.
      // Note that struct columns are actually nullable in two ways. For a column `foo`:
      // {foo: null} and {} are both valid, and are both written to the final table as a SQL NULL (_not_ a
      // JSON null).
      // JSON_QUERY(JSON'{}', '$."foo"') returns a SQL null.
      // JSON_QUERY(JSON'{"foo": null}', '$."foo"') returns a JSON null.
      return new StringSubstitutor(Map.of("column_name", escapeColumnNameForJsonPath(column.getOriginalName()))).replace(
          """
          PARSE_JSON(CASE
            WHEN JSON_QUERY(`_airbyte_data`, '$."${column_name}"') IS NULL
              OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$."${column_name}"'), wide_number_mode=>'round')) != 'object'
              THEN NULL
            ELSE JSON_QUERY(`_airbyte_data`, '$."${column_name}"')
          END, wide_number_mode=>'round')
          """);
    }

    if (airbyteType instanceof Array) {
      // Much like the Struct case above, arrays need special handling.
      return new StringSubstitutor(Map.of("column_name", escapeColumnNameForJsonPath(column.getOriginalName()))).replace(
          """
          PARSE_JSON(CASE
            WHEN JSON_QUERY(`_airbyte_data`, '$."${column_name}"') IS NULL
              OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$."${column_name}"'), wide_number_mode=>'round')) != 'array'
              THEN NULL
            ELSE JSON_QUERY(`_airbyte_data`, '$."${column_name}"')
          END, wide_number_mode=>'round')
          """);
    }

    if (airbyteType instanceof UnsupportedOneOf || airbyteType == AirbyteProtocolType.UNKNOWN) {
      // JSON_QUERY returns a SQL null if the field contains a JSON null, so we actually parse the
      // airbyte_data to json
      // and json_query it directly (which preserves nulls correctly).
      return new StringSubstitutor(Map.of("column_name", escapeColumnNameForJsonPath(column.getOriginalName()))).replace(
          """
          JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."${column_name}"')
          """);
    }

    if (airbyteType == AirbyteProtocolType.STRING) {
      // Special case String to only use json value for type string and parse the json for others
      // Naive json_value returns NULL for object/array values and json_query adds escaped quotes to the
      // string.
      return new StringSubstitutor(Map.of("column_name", escapeColumnNameForJsonPath(column.getOriginalName()))).replace(
          """
          (CASE
                WHEN JSON_QUERY(`_airbyte_data`, '$."${column_name}"') IS NULL
                  OR JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$."${column_name}"'), wide_number_mode=>'round')) != 'string'
                  THEN JSON_QUERY(`_airbyte_data`, '$."${column_name}"')
              ELSE
              JSON_VALUE(`_airbyte_data`, '$."${column_name}"')
            END)
          """);
    }

    final StandardSQLTypeName dialectType = toDialectType(airbyteType);
    final var baseTyping = "JSON_VALUE(`_airbyte_data`, '$.\"" + escapeColumnNameForJsonPath(column.getOriginalName()) + "\"')";
    if (dialectType == StandardSQLTypeName.STRING) {
      // json_value implicitly returns a string, so we don't need to cast it.
      return baseTyping;
    } else {
      // SAFE_CAST is actually a massive performance hit, so we should skip it if we can.
      return cast(baseTyping, dialectType.name(), forceSafeCast);
    }
  }

  // TODO maybe make this a BiMap and elevate this method and its inverse (toDestinationSQLType?) to
  // the SQLGenerator?
  public static StandardSQLTypeName toDialectType(final AirbyteProtocolType airbyteProtocolType) {
    return switch (airbyteProtocolType) {
      case STRING, TIME_WITH_TIMEZONE -> StandardSQLTypeName.STRING;
      case NUMBER -> StandardSQLTypeName.NUMERIC;
      case INTEGER -> StandardSQLTypeName.INT64;
      case BOOLEAN -> StandardSQLTypeName.BOOL;
      case TIMESTAMP_WITH_TIMEZONE -> StandardSQLTypeName.TIMESTAMP;
      case TIMESTAMP_WITHOUT_TIMEZONE -> StandardSQLTypeName.DATETIME;
      case TIME_WITHOUT_TIMEZONE -> StandardSQLTypeName.TIME;
      case DATE -> StandardSQLTypeName.DATE;
      case UNKNOWN -> StandardSQLTypeName.JSON;
    };
  }

  @Override
  public Sql createTable(final StreamConfig stream, final String suffix, final boolean force) {
    final String columnDeclarations = columnsAndTypes(stream);
    final String clusterConfig = clusteringColumns(stream).stream()
        .map(c -> StringUtils.wrap(c, QUOTE))
        .collect(joining(", "));
    final String forceCreateTable = force ? "OR REPLACE" : "";

    return Sql.of(new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "final_namespace", stream.getId().finalNamespace(QUOTE),
        "force_create_table", forceCreateTable,
        "final_table_id", stream.getId().finalTableId(QUOTE, suffix),
        "column_declarations", columnDeclarations,
        "cluster_config", clusterConfig)).replace(
            """
            CREATE ${force_create_table} TABLE ${project_id}.${final_table_id} (
              _airbyte_raw_id STRING NOT NULL,
              _airbyte_extracted_at TIMESTAMP NOT NULL,
              _airbyte_meta JSON NOT NULL,
            ${column_declarations}
            )
            PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
            CLUSTER BY ${cluster_config};
            """));
  }

  static List<String> clusteringColumns(final StreamConfig stream) {
    final List<String> clusterColumns = new ArrayList<>();
    if (stream.getDestinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      // We're doing de-duping, therefore we have a primary key.
      // Cluster on the first 3 PK columns since BigQuery only allows up to 4 clustering columns,
      // and we're always clustering on _airbyte_extracted_at
      stream.getPrimaryKey().stream().limit(3).forEach(columnId -> {
        clusterColumns.add(columnId.getName());
      });
    }
    clusterColumns.add("_airbyte_extracted_at");
    return clusterColumns;
  }

  private String columnsAndTypes(final StreamConfig stream) {
    return stream.getColumns().entrySet().stream()
        .map(column -> String.join(" ", column.getKey().name(QUOTE), toDialectType(column.getValue()).name()))
        .collect(joining(",\n"));
  }

  @Override
  public Sql prepareTablesForSoftReset(final StreamConfig stream) {
    // Bigquery can't run DDL in a transaction, so these are separate transactions.
    return Sql.concat(
        // If a previous sync failed to delete the soft reset temp table (unclear why this happens),
        // AND this sync is trying to change the clustering config, then we need to manually drop the soft
        // reset temp table.
        // Even though we're using CREATE OR REPLACE TABLE, bigquery will still complain about the
        // clustering config being changed.
        // So we explicitly drop the soft reset temp table first.
        dropTableIfExists(stream, SOFT_RESET_SUFFIX),
        createTable(stream, SOFT_RESET_SUFFIX, true),
        clearLoadedAt(stream.getId()));
  }

  public Sql dropTableIfExists(final StreamConfig stream, final String suffix) {
    return Sql.of(new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "table_id", stream.getId().finalTableId(QUOTE, suffix)))
            .replace("""
                     DROP TABLE IF EXISTS ${project_id}.${table_id};
                     """));
  }

  @Override
  public Sql clearLoadedAt(final StreamId streamId) {
    return Sql.of(new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "raw_table_id", streamId.rawTableId(QUOTE)))
            .replace("""
                     UPDATE ${project_id}.${raw_table_id} SET _airbyte_loaded_at = NULL WHERE 1=1;
                     """));
  }

  @Override
  public Sql updateTable(final StreamConfig stream,
                         final String finalSuffix,
                         final Optional<Instant> minRawTimestamp,
                         final boolean useExpensiveSaferCasting) {
    final String handleNewRecords;
    if (stream.getDestinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      handleNewRecords = upsertNewRecords(stream, finalSuffix, useExpensiveSaferCasting, minRawTimestamp);
    } else {
      handleNewRecords = insertNewRecords(stream, finalSuffix, useExpensiveSaferCasting, minRawTimestamp);
    }
    final String commitRawTable = commitRawTable(stream.getId(), minRawTimestamp);

    return transactionally(handleNewRecords, commitRawTable);
  }

  private String insertNewRecords(final StreamConfig stream,
                                  final String finalSuffix,
                                  final boolean forceSafeCasting,
                                  final Optional<Instant> minRawTimestamp) {
    final String columnList = stream.getColumns().keySet().stream().map(quotedColumnId -> quotedColumnId.name(QUOTE) + ",").collect(joining("\n"));
    final String extractNewRawRecords = extractNewRawRecords(stream, forceSafeCasting, minRawTimestamp);

    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "final_table_id", stream.getId().finalTableId(QUOTE, finalSuffix),
        "column_list", columnList,
        "extractNewRawRecords", extractNewRawRecords)).replace(
            """
            INSERT INTO ${project_id}.${final_table_id}
            (
            ${column_list}
              _airbyte_meta,
              _airbyte_raw_id,
              _airbyte_extracted_at
            )
            ${extractNewRawRecords};""");
  }

  private String upsertNewRecords(final StreamConfig stream,
                                  final String finalSuffix,
                                  final boolean forceSafeCasting,
                                  final Optional<Instant> minRawTimestamp) {
    final String pkEquivalent = stream.getPrimaryKey().stream().map(pk -> {
      final String quotedPk = pk.name(QUOTE);
      // either the PKs are equal, or they're both NULL
      return "(target_table." + quotedPk + " = new_record." + quotedPk
          + " OR (target_table." + quotedPk + " IS NULL AND new_record." + quotedPk + " IS NULL))";
    }).collect(joining(" AND "));

    final String columnList = stream.getColumns().keySet().stream()
        .map(quotedColumnId -> quotedColumnId.name(QUOTE) + ",")
        .collect(joining("\n"));
    final String newRecordColumnList = stream.getColumns().keySet().stream()
        .map(quotedColumnId -> "new_record." + quotedColumnId.name(QUOTE) + ",")
        .collect(joining("\n"));
    final String extractNewRawRecords = extractNewRawRecords(stream, forceSafeCasting, minRawTimestamp);

    final String cursorComparison;
    if (stream.getCursor().isPresent()) {
      final String cursor = stream.getCursor().get().name(QUOTE);
      // Build a condition for "new_record is more recent than target_table":
      cursorComparison =
          // First, compare the cursors.
          "(target_table." + cursor + " < new_record." + cursor
          // Then, break ties with extracted_at. (also explicitly check for both new_record and final table
          // having null cursor
          // because NULL != NULL in SQL)
              + " OR (target_table." + cursor + " = new_record." + cursor
              + " AND target_table._airbyte_extracted_at < new_record._airbyte_extracted_at)"
              + " OR (target_table." + cursor + " IS NULL AND new_record." + cursor
              + " IS NULL AND target_table._airbyte_extracted_at < new_record._airbyte_extracted_at)"
              // Or, if the final table has null cursor but new_record has non-null cursor, then take the new
              // record.
              + " OR (target_table." + cursor + " IS NULL AND new_record." + cursor + " IS NOT NULL))";
    } else {
      // If there's no cursor, then we just take the most-recently-emitted record
      cursorComparison = "target_table._airbyte_extracted_at < new_record._airbyte_extracted_at";
    }

    final String cdcDeleteClause;
    final String cdcSkipInsertClause;
    if (stream.getColumns().containsKey(CDC_DELETED_AT_COLUMN)) {
      // Execute CDC deletions if there's already a record
      cdcDeleteClause = "WHEN MATCHED AND new_record._ab_cdc_deleted_at IS NOT NULL AND " + cursorComparison + " THEN DELETE";
      // And skip insertion entirely if there's no matching record.
      // (This is possible if a single T+D batch contains both an insertion and deletion for the same PK)
      cdcSkipInsertClause = "AND new_record._ab_cdc_deleted_at IS NULL";
    } else {
      cdcDeleteClause = "";
      cdcSkipInsertClause = "";
    }

    final String columnAssignments = stream.getColumns().keySet().stream()
        .map(airbyteType -> {
          final String column = airbyteType.name(QUOTE);
          return column + " = new_record." + column + ",";
        }).collect(joining("\n"));

    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "final_table_id", stream.getId().finalTableId(QUOTE, finalSuffix),
        "extractNewRawRecords", extractNewRawRecords,
        "pkEquivalent", pkEquivalent,
        "cdcDeleteClause", cdcDeleteClause,
        "cursorComparison", cursorComparison,
        "columnAssignments", columnAssignments,
        "cdcSkipInsertClause", cdcSkipInsertClause,
        "column_list", columnList,
        "newRecordColumnList", newRecordColumnList)).replace(
            """
            MERGE ${project_id}.${final_table_id} target_table
            USING (
              ${extractNewRawRecords}
            ) new_record
            ON ${pkEquivalent}
            ${cdcDeleteClause}
            WHEN MATCHED AND ${cursorComparison} THEN UPDATE SET
              ${columnAssignments}
              _airbyte_meta = new_record._airbyte_meta,
              _airbyte_raw_id = new_record._airbyte_raw_id,
              _airbyte_extracted_at = new_record._airbyte_extracted_at
            WHEN NOT MATCHED ${cdcSkipInsertClause} THEN INSERT (
              ${column_list}
              _airbyte_meta,
              _airbyte_raw_id,
              _airbyte_extracted_at
            ) VALUES (
              ${newRecordColumnList}
              new_record._airbyte_meta,
              new_record._airbyte_raw_id,
              new_record._airbyte_extracted_at
            );""");
  }

  /**
   * A SQL SELECT statement that extracts new records from the raw table, casts their columns, and
   * builds their airbyte_meta column.
   * <p>
   * In dedup mode: Also extracts all raw CDC deletion records (for tombstoning purposes) and dedupes
   * the records (since we only need the most-recent record to upsert).
   */
  private String extractNewRawRecords(final StreamConfig stream,
                                      final boolean forceSafeCasting,
                                      final Optional<Instant> minRawTimestamp) {
    final String columnCasts = stream.getColumns().entrySet().stream().map(
        col -> extractAndCast(col.getKey(), col.getValue(), forceSafeCasting) + " as " + col.getKey().name(QUOTE) + ",")
        .collect(joining("\n"));
    final String columnErrors;
    if (forceSafeCasting) {
      columnErrors = "[" + stream.getColumns().entrySet().stream().map(
          col -> new StringSubstitutor(Map.of(
              "raw_col_name", escapeColumnNameForJsonPath(col.getKey().getOriginalName()),
              "col_type", toDialectType(col.getValue()).name(),
              "json_extract", extractAndCast(col.getKey(), col.getValue(), true))).replace(
                  // Explicitly parse json here. This is safe because we're not using the actual value anywhere,
                  // and necessary because json_query
                  """
                  CASE
                    WHEN (JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."${raw_col_name}"') IS NOT NULL)
                      AND (JSON_TYPE(JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."${raw_col_name}"')) != 'null')
                      AND (${json_extract} IS NULL)
                      THEN 'Problem with `${raw_col_name}`'
                    ELSE NULL
                  END"""))
          .collect(joining(",\n")) + "]";
    } else {
      // We're not safe casting, so any error should throw an exception and trigger the safe cast logic
      columnErrors = "[]";
    }

    final String columnList = stream.getColumns().keySet().stream().map(quotedColumnId -> quotedColumnId.name(QUOTE) + ",").collect(joining("\n"));
    final String extractedAtCondition = buildExtractedAtCondition(minRawTimestamp);

    if (stream.getDestinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      // When deduping, we need to dedup the raw records. Note the row_number() invocation in the SQL
      // statement. Do the same extract+cast CTE + airbyte_meta construction as in non-dedup mode, but
      // then add a row_number column so that we only take the most-recent raw record for each PK.

      // We also explicitly include old CDC deletion records, which act as tombstones to correctly delete
      // out-of-order records.
      String cdcConditionalOrIncludeStatement = "";
      if (stream.getColumns().containsKey(CDC_DELETED_AT_COLUMN)) {
        cdcConditionalOrIncludeStatement = """
                                           OR (
                                             _airbyte_loaded_at IS NOT NULL
                                             AND JSON_VALUE(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NOT NULL
                                           )
                                           """;
      }

      final String pkList = stream.getPrimaryKey().stream().map(columnId -> columnId.name(QUOTE)).collect(joining(","));
      final String cursorOrderClause = stream.getCursor()
          .map(cursorId -> cursorId.name(QUOTE) + " DESC NULLS LAST,")
          .orElse("");

      return new StringSubstitutor(Map.of(
          "project_id", '`' + projectId + '`',
          "raw_table_id", stream.getId().rawTableId(QUOTE),
          "column_casts", columnCasts,
          "column_errors", columnErrors,
          "cdcConditionalOrIncludeStatement", cdcConditionalOrIncludeStatement,
          "extractedAtCondition", extractedAtCondition,
          "column_list", columnList,
          "pk_list", pkList,
          "cursor_order_clause", cursorOrderClause)).replace(
              """
              WITH intermediate_data AS (
                SELECT
              ${column_casts}
                ${column_errors} AS column_errors,
                _airbyte_raw_id,
                _airbyte_extracted_at
                FROM ${project_id}.${raw_table_id}
                WHERE (
                    _airbyte_loaded_at IS NULL
                    ${cdcConditionalOrIncludeStatement}
                  ) ${extractedAtCondition}
              ), new_records AS (
                SELECT
                ${column_list}
                  to_json(struct(COALESCE((SELECT ARRAY_AGG(unnested_column_errors IGNORE NULLS) FROM UNNEST(column_errors) unnested_column_errors), []) AS errors)) AS _airbyte_meta,
                  _airbyte_raw_id,
                  _airbyte_extracted_at
                FROM intermediate_data
              ), numbered_rows AS (
                SELECT *, row_number() OVER (
                  PARTITION BY ${pk_list} ORDER BY ${cursor_order_clause} `_airbyte_extracted_at` DESC
                ) AS row_number
                FROM new_records
              )
              SELECT ${column_list} _airbyte_meta, _airbyte_raw_id, _airbyte_extracted_at
              FROM numbered_rows
              WHERE row_number = 1""");
    } else {
      // When not deduplicating, we just need to handle type casting.
      // Extract+cast the not-yet-loaded records in a CTE, then select that CTE and build airbyte_meta.

      return new StringSubstitutor(Map.of(
          "project_id", '`' + projectId + '`',
          "raw_table_id", stream.getId().rawTableId(QUOTE),
          "column_casts", columnCasts,
          "column_errors", columnErrors,
          "extractedAtCondition", extractedAtCondition,
          "column_list", columnList)).replace(
              """
              WITH intermediate_data AS (
                SELECT
              ${column_casts}
                ${column_errors} AS column_errors,
                _airbyte_raw_id,
                _airbyte_extracted_at
                FROM ${project_id}.${raw_table_id}
                WHERE
                  _airbyte_loaded_at IS NULL
                  ${extractedAtCondition}
              )
              SELECT
              ${column_list}
                to_json(struct(COALESCE((SELECT ARRAY_AGG(unnested_column_errors IGNORE NULLS) FROM UNNEST(column_errors) unnested_column_errors), []) AS errors)) AS _airbyte_meta,
                _airbyte_raw_id,
                _airbyte_extracted_at
              FROM intermediate_data""");
    }
  }

  private static String buildExtractedAtCondition(final Optional<Instant> minRawTimestamp) {
    return minRawTimestamp
        .map(ts -> " AND _airbyte_extracted_at > '" + ts + "'")
        .orElse("");
  }

  @VisibleForTesting
  String commitRawTable(final StreamId id, final Optional<Instant> minRawTimestamp) {
    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "raw_table_id", id.rawTableId(QUOTE),
        "extractedAtCondition", buildExtractedAtCondition(minRawTimestamp))).replace(
            """
            UPDATE ${project_id}.${raw_table_id}
            SET `_airbyte_loaded_at` = CURRENT_TIMESTAMP()
            WHERE `_airbyte_loaded_at` IS NULL
              ${extractedAtCondition}
            ;""");
  }

  @Override
  public Sql overwriteFinalTable(final StreamId streamId, final String finalSuffix) {
    final StringSubstitutor substitutor = new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "final_table_id", streamId.finalTableId(QUOTE),
        "tmp_final_table", streamId.finalTableId(QUOTE, finalSuffix),
        "real_final_table", streamId.finalName(QUOTE)));
    return separately(
        substitutor.replace("DROP TABLE IF EXISTS ${project_id}.${final_table_id};"),
        substitutor.replace("ALTER TABLE ${project_id}.${tmp_final_table} RENAME TO ${real_final_table};"));
  }

  private String wrapAndQuote(final String namespace, final String tableName) {
    return Stream.of(namespace, tableName)
        .map(part -> StringUtils.wrap(part, QUOTE))
        .collect(joining("."));
  }

  @Override
  public Sql createSchema(final String schema) {
    return Sql.of(new StringSubstitutor(Map.of("schema", StringUtils.wrap(schema, QUOTE),
        "project_id", StringUtils.wrap(projectId, QUOTE),
        "dataset_location", datasetLocation))
            .replace("CREATE SCHEMA IF NOT EXISTS ${project_id}.${schema} OPTIONS(location=\"${dataset_location}\");"));
  }

  @Override
  public Sql migrateFromV1toV2(final StreamId streamId, final String namespace, final String tableName) {
    return Sql.of(new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "v2_raw_table", streamId.rawTableId(QUOTE),
        "v1_raw_table", wrapAndQuote(namespace, tableName))).replace(
            """
            CREATE OR REPLACE TABLE ${project_id}.${v2_raw_table} (
              _airbyte_raw_id STRING,
              _airbyte_data STRING,
              _airbyte_extracted_at TIMESTAMP,
              _airbyte_loaded_at TIMESTAMP
            )
            PARTITION BY DATE(_airbyte_extracted_at)
            CLUSTER BY _airbyte_extracted_at
            AS (
                SELECT
                    _airbyte_ab_id AS _airbyte_raw_id,
                    _airbyte_data AS _airbyte_data,
                    _airbyte_emitted_at AS _airbyte_extracted_at,
                    CAST(NULL AS TIMESTAMP) AS _airbyte_loaded_at
                FROM ${project_id}.${v1_raw_table}
            );
            """));
  }

  /**
   * Does two things: escape single quotes (for use inside sql string literals),and escape double
   * quotes (for use inside JSON paths). For example, if a column name is foo'bar"baz, then we want to
   * end up with something like {@code SELECT JSON_QUERY(..., '$."foo\'bar\\"baz"')}. Note the
   * single-backslash for single-quotes (needed for SQL) and the double-backslash for double-quotes
   * (needed for JSON path).
   */
  private String escapeColumnNameForJsonPath(final String stringContents) {
    // This is not a place of honor.
    return stringContents
        // Consider the JSON blob {"foo\\bar": 42}.
        // This is an object with key foo\bar.
        // The JSONPath for this is (something like...?) $."foo\\bar" (i.e. 2 backslashes).
        // TODO is that jsonpath correct?
        // When we represent that path as a SQL string, the backslashes are doubled (to 4): '$."foo\\\\bar"'
        // And we're writing that in a Java string, so we have to type out 8 backslashes:
        // "'$.\"foo\\\\\\\\bar\"'"
        .replace("\\", "\\\\\\\\")
        // Similar situation here:
        // a literal " needs to be \" in a JSONPath: $."foo\"bar"
        // which is \\" in a SQL string: '$."foo\\"bar"'
        // The backslashes become \\\\ in java, and the quote becomes \": "'$.\"foo\\\\\"bar\"'"
        .replace("\"", "\\\\\"")
        // Here we're escaping a SQL string, so we only need a single backslash (which is 2, beacuse Java).
        .replace("'", "\\'");
  }

  private static String cast(final String content, final String asType, final boolean useSafeCast) {
    final var open = useSafeCast ? "SAFE_CAST(" : "CAST(";
    return wrap(open, content + " as " + asType, ")");
  }

  private static String wrap(final String open, final String content, final String close) {
    return open + content + close;
  }

}
