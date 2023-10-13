/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils.containsAllIgnoreCase;
import static io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils.containsIgnoreCase;
import static io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils.matchingKey;
import static java.util.stream.Collectors.joining;

import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Field.Mode;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TimePartitioning;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.AlterTableReport;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.TableNotMigratedException;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.text.StringSubstitutor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQuerySqlGenerator implements SqlGenerator<TableDefinition> {

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
      return new StringSubstitutor(Map.of("column_name", escapeColumnNameForJsonPath(column.originalName()))).replace(
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
      return new StringSubstitutor(Map.of("column_name", escapeColumnNameForJsonPath(column.originalName()))).replace(
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
      return new StringSubstitutor(Map.of("column_name", escapeColumnNameForJsonPath(column.originalName()))).replace(
          """
          JSON_QUERY(PARSE_JSON(`_airbyte_data`, wide_number_mode=>'round'), '$."${column_name}"')
          """);
    }

    if (airbyteType == AirbyteProtocolType.STRING) {
      // Special case String to only use json value for type string and parse the json for others
      // Naive json_value returns NULL for object/array values and json_query adds escaped quotes to the
      // string.
      return new StringSubstitutor(Map.of("column_name", escapeColumnNameForJsonPath(column.originalName()))).replace(
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
    final var baseTyping = "JSON_VALUE(`_airbyte_data`, '$.\"" + escapeColumnNameForJsonPath(column.originalName()) + "\"')";
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
  public StandardSQLTypeName toDialectType(final AirbyteProtocolType airbyteProtocolType) {
    return switch (airbyteProtocolType) {
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
  public String createTable(final StreamConfig stream, final String suffix, final boolean force) {
    final String columnDeclarations = columnsAndTypes(stream);
    final String clusterConfig = clusteringColumns(stream).stream()
        .map(c -> StringUtils.wrap(c, QUOTE))
        .collect(joining(", "));
    final String forceCreateTable = force ? "OR REPLACE" : "";

    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "final_namespace", stream.id().finalNamespace(QUOTE),
        "dataset_location", datasetLocation,
        "force_create_table", forceCreateTable,
        "final_table_id", stream.id().finalTableId(QUOTE, suffix),
        "column_declarations", columnDeclarations,
        "cluster_config", clusterConfig)).replace(
            """
            CREATE SCHEMA IF NOT EXISTS ${project_id}.${final_namespace}
            OPTIONS(location="${dataset_location}");

            CREATE ${force_create_table} TABLE ${project_id}.${final_table_id} (
              _airbyte_raw_id STRING NOT NULL,
              _airbyte_extracted_at TIMESTAMP NOT NULL,
              _airbyte_meta JSON NOT NULL,
            ${column_declarations}
            )
            PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
            CLUSTER BY ${cluster_config};
            """);
  }

  private List<String> clusteringColumns(final StreamConfig stream) {
    final List<String> clusterColumns = new ArrayList<>();
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      // We're doing de-duping, therefore we have a primary key.
      // Cluster on the first 3 PK columns since BigQuery only allows up to 4 clustering columns,
      // and we're always clustering on _airbyte_extracted_at
      stream.primaryKey().stream().limit(3).forEach(columnId -> {
        clusterColumns.add(columnId.name());
      });
    }
    clusterColumns.add("_airbyte_extracted_at");
    return clusterColumns;
  }

  private String columnsAndTypes(final StreamConfig stream) {
    return stream.columns().entrySet().stream()
        .map(column -> String.join(" ", column.getKey().name(QUOTE), toDialectType(column.getValue()).name()))
        .collect(joining(",\n"));
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream,
                                                   final TableDefinition existingTable)
      throws TableNotMigratedException {
    final var alterTableReport = buildAlterTableReport(stream, existingTable);
    boolean tableClusteringMatches = false;
    boolean tablePartitioningMatches = false;
    if (existingTable instanceof final StandardTableDefinition standardExistingTable) {
      tableClusteringMatches = clusteringMatches(stream, standardExistingTable);
      tablePartitioningMatches = partitioningMatches(standardExistingTable);
    }
    LOGGER.info("Alter Table Report {} {} {}; Clustering {}; Partitioning {}",
        alterTableReport.columnsToAdd(),
        alterTableReport.columnsToRemove(),
        alterTableReport.columnsToChangeType(),
        tableClusteringMatches,
        tablePartitioningMatches);

    return alterTableReport.isNoOp() && tableClusteringMatches && tablePartitioningMatches;
  }

  @VisibleForTesting
  public boolean clusteringMatches(final StreamConfig stream, final StandardTableDefinition existingTable) {
    return existingTable.getClustering() != null
        && containsAllIgnoreCase(
            new HashSet<>(existingTable.getClustering().getFields()),
            clusteringColumns(stream));
  }

  @VisibleForTesting
  public boolean partitioningMatches(final StandardTableDefinition existingTable) {
    return existingTable.getTimePartitioning() != null
        && existingTable.getTimePartitioning()
            .getField()
            .equalsIgnoreCase("_airbyte_extracted_at")
        && TimePartitioning.Type.DAY.equals(existingTable.getTimePartitioning().getType());
  }

  public AlterTableReport buildAlterTableReport(final StreamConfig stream, final TableDefinition existingTable) {
    final Set<String> pks = getPks(stream);

    final Map<String, StandardSQLTypeName> streamSchema = stream.columns().entrySet().stream()
        .collect(Collectors.toMap(
            entry -> entry.getKey().name(),
            entry -> toDialectType(entry.getValue())));

    final Map<String, StandardSQLTypeName> existingSchema = existingTable.getSchema().getFields().stream()
        .collect(Collectors.toMap(
            field -> field.getName(),
            field -> field.getType().getStandardType()));

    // Columns in the StreamConfig that don't exist in the TableDefinition
    final Set<String> columnsToAdd = streamSchema.keySet().stream()
        .filter(name -> !containsIgnoreCase(existingSchema.keySet(), name))
        .collect(Collectors.toSet());

    // Columns in the current schema that are no longer in the StreamConfig
    final Set<String> columnsToRemove = existingSchema.keySet().stream()
        .filter(name -> !containsIgnoreCase(streamSchema.keySet(), name) && !containsIgnoreCase(
            JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS, name))
        .collect(Collectors.toSet());

    // Columns that are typed differently than the StreamConfig
    final Set<String> columnsToChangeType = Stream.concat(
        streamSchema.keySet().stream()
            // If it's not in the existing schema, it should already be in the columnsToAdd Set
            .filter(name -> {
              // Big Query Columns are case-insensitive, first find the correctly cased key if it exists
              return matchingKey(existingSchema.keySet(), name)
                  // if it does exist, only include it in this set if the type (the value in each respective map)
                  // is different between the stream and existing schemas
                  .map(key -> !existingSchema.get(key).equals(streamSchema.get(name)))
                  // if there is no matching key, then don't include it because it is probably already in columnsToAdd
                  .orElse(false);
            }),

        // OR columns that used to have a non-null constraint and shouldn't
        // (https://github.com/airbytehq/airbyte/pull/31082)
        existingTable.getSchema().getFields().stream()
            .filter(field -> pks.contains(field.getName()))
            .filter(field -> field.getMode() == Mode.REQUIRED)
            .map(Field::getName))
        .collect(Collectors.toSet());

    final boolean isDestinationV2Format = schemaContainAllFinalTableV2AirbyteColumns(existingSchema.keySet());

    return new AlterTableReport(columnsToAdd, columnsToRemove, columnsToChangeType, isDestinationV2Format);
  }

  /**
   * Checks the schema to determine whether the table contains all expected final table airbyte
   * columns
   *
   * @param columnNames the column names of the schema to check
   * @return whether all the {@link JavaBaseConstants#V2_FINAL_TABLE_METADATA_COLUMNS} are present
   */
  @VisibleForTesting
  public static boolean schemaContainAllFinalTableV2AirbyteColumns(final Collection<String> columnNames) {
    return JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS.stream()
        .allMatch(column -> containsIgnoreCase(columnNames, column));
  }

  @Override
  public String softReset(final StreamConfig stream) {
    // If a previous sync failed to delete the soft reset temp table (unclear why this happens),
    // AND this sync is trying to change the clustering config, then we need to manually drop the soft
    // reset temp table.
    // Even though we're using CREATE OR REPLACE TABLE, bigquery will still complain about the
    // clustering config being changed.
    // So we explicitly drop the soft reset temp table first.
    final String dropTempTable = dropTableIfExists(stream, SOFT_RESET_SUFFIX);
    final String createTempTable = createTable(stream, SOFT_RESET_SUFFIX, true);
    final String clearLoadedAt = clearLoadedAt(stream.id());
    final String rebuildInTempTable = updateTable(stream, SOFT_RESET_SUFFIX, false);
    final String overwriteFinalTable = overwriteFinalTable(stream.id(), SOFT_RESET_SUFFIX);
    return String.join("\n", dropTempTable, createTempTable, clearLoadedAt, rebuildInTempTable, overwriteFinalTable);
  }

  public String dropTableIfExists(final StreamConfig stream, final String suffix) {
    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "table_id", stream.id().finalTableId(QUOTE, suffix)))
            .replace("""
                     DROP TABLE IF EXISTS ${project_id}.${table_id};
                     """);
  }

  private String clearLoadedAt(final StreamId streamId) {
    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "raw_table_id", streamId.rawTableId(QUOTE)))
            .replace("""
                     UPDATE ${project_id}.${raw_table_id} SET _airbyte_loaded_at = NULL WHERE 1=1;
                     """);
  }

  @Override
  public String updateTable(final StreamConfig stream, final String finalSuffix) {
    return updateTable(stream, finalSuffix, true);
  }

  private String updateTableQueryBuilder(final StreamConfig stream,
                                         final String finalSuffix,
                                         final boolean verifyPrimaryKeys,
                                         final boolean forceSafeCasting) {
    final String insertNewRecords = insertNewRecords(stream, finalSuffix, stream.columns(), forceSafeCasting);
    String dedupFinalTable = "";
    String cdcDeletes = "";
    String dedupRawTable = "";
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      dedupRawTable = dedupRawTable(stream.id(), finalSuffix);
      // If we're in dedup mode, then we must have a cursor
      dedupFinalTable = dedupFinalTable(stream.id(), finalSuffix, stream.primaryKey(), stream.cursor());
      cdcDeletes = cdcDeletes(stream, finalSuffix, stream.columns(), forceSafeCasting);
    }
    final String commitRawTable = commitRawTable(stream.id());

    return new StringSubstitutor(Map.of(
        "insert_new_records", insertNewRecords,
        "dedup_final_table", dedupFinalTable,
        "cdc_deletes", cdcDeletes,
        "dedupe_raw_table", dedupRawTable,
        "commit_raw_table", commitRawTable)).replace(
            """
            BEGIN TRANSACTION;
            ${insert_new_records}
            ${dedup_final_table}
            ${dedupe_raw_table}
            ${cdc_deletes}
            ${commit_raw_table}
            COMMIT TRANSACTION;
            """);
  }

  private String updateTable(final StreamConfig stream, final String finalSuffix, final boolean verifyPrimaryKeys) {
    final var unsafeUpdate = updateTableQueryBuilder(stream, finalSuffix, verifyPrimaryKeys, false);
    final var safeUpdate = updateTableQueryBuilder(stream, finalSuffix, verifyPrimaryKeys, true);
    final String pkVarDeclaration = verifyPrimaryKeys ? "DECLARE missing_pk_count INT64;" : "";
    return new StringSubstitutor(Map.of("unsafe_update", unsafeUpdate, "safe_update", safeUpdate, "pk_var_declaration", pkVarDeclaration)).replace(
        """
        ${pk_var_declaration}

        BEGIN

        ${unsafe_update}

        EXCEPTION WHEN ERROR THEN
        ROLLBACK TRANSACTION;

        ${safe_update}

        END;

        """);
  }

  @VisibleForTesting
  String insertNewRecords(final StreamConfig stream,
                          final String finalSuffix,
                          final LinkedHashMap<ColumnId, AirbyteType> streamColumns,
                          final boolean forceSafeCasting) {
    final String columnCasts = streamColumns.entrySet().stream().map(
        col -> extractAndCast(col.getKey(), col.getValue(), forceSafeCasting) + " as " + col.getKey().name(QUOTE) + ",")
        .collect(joining("\n"));
    final String columnErrors;
    if (forceSafeCasting) {
      columnErrors = "[" + streamColumns.entrySet().stream().map(
          col -> new StringSubstitutor(Map.of(
              "raw_col_name", escapeColumnNameForJsonPath(col.getKey().originalName()),
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

    final String columnList = streamColumns.keySet().stream().map(quotedColumnId -> quotedColumnId.name(QUOTE) + ",").collect(joining("\n"));

    String cdcConditionalOrIncludeStatement = "";
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP && streamColumns.containsKey(CDC_DELETED_AT_COLUMN)) {
      cdcConditionalOrIncludeStatement = """
                                         OR (
                                           _airbyte_loaded_at IS NOT NULL
                                           AND JSON_VALUE(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NOT NULL
                                         )
                                         """;
    }

    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "raw_table_id", stream.id().rawTableId(QUOTE),
        "final_table_id", stream.id().finalTableId(QUOTE, finalSuffix),
        "column_casts", columnCasts,
        "column_errors", columnErrors,
        "cdcConditionalOrIncludeStatement", cdcConditionalOrIncludeStatement,
        "column_list", columnList)).replace(
            """
            INSERT INTO ${project_id}.${final_table_id}
            (
            ${column_list}
              _airbyte_meta,
              _airbyte_raw_id,
              _airbyte_extracted_at
            )
            WITH intermediate_data AS (
              SELECT
            ${column_casts}
              ${column_errors} AS column_errors,
              _airbyte_raw_id,
              _airbyte_extracted_at
              FROM ${project_id}.${raw_table_id}
              WHERE
                _airbyte_loaded_at IS NULL
                ${cdcConditionalOrIncludeStatement}
            )
            SELECT
            ${column_list}
              to_json(struct(COALESCE((SELECT ARRAY_AGG(unnested_column_errors IGNORE NULLS) FROM UNNEST(column_errors) unnested_column_errors), []) AS errors)) AS _airbyte_meta,
              _airbyte_raw_id,
              _airbyte_extracted_at
            FROM intermediate_data;""");
  }

  @VisibleForTesting
  String dedupFinalTable(final StreamId id,
                         final String finalSuffix,
                         final List<ColumnId> primaryKey,
                         final Optional<ColumnId> cursor) {
    final String pkList = primaryKey.stream().map(columnId -> columnId.name(QUOTE)).collect(joining(","));
    final String cursorOrderClause = cursor
        .map(cursorId -> cursorId.name(QUOTE) + " DESC NULLS LAST,")
        .orElse("");

    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "final_table_id", id.finalTableId(QUOTE, finalSuffix),
        "pk_list", pkList,
        "cursor_order_clause", cursorOrderClause)).replace(
            """
            DELETE FROM ${project_id}.${final_table_id}
            WHERE
              `_airbyte_raw_id` IN (
                SELECT `_airbyte_raw_id` FROM (
                  SELECT `_airbyte_raw_id`, row_number() OVER (
                    PARTITION BY ${pk_list} ORDER BY ${cursor_order_clause} `_airbyte_extracted_at` DESC
                  ) as row_number FROM ${project_id}.${final_table_id}
                )
                WHERE row_number != 1
              )
            ;""");
  }

  @VisibleForTesting
  String cdcDeletes(final StreamConfig stream,
                    final String finalSuffix,
                    final LinkedHashMap<ColumnId, AirbyteType> streamColumns,
                    final boolean forceSafeCasting) {

    if (stream.destinationSyncMode() != DestinationSyncMode.APPEND_DEDUP) {
      return "";
    }

    if (!streamColumns.containsKey(CDC_DELETED_AT_COLUMN)) {
      return "";
    }

    final String pkList = stream.primaryKey().stream().map(columnId -> columnId.name(QUOTE)).collect(joining(","));
    final String pkCasts =
        stream.primaryKey().stream().map(pk -> extractAndCast(pk, streamColumns.get(pk), forceSafeCasting)).collect(joining(",\n"));

    // we want to grab IDs for deletion from the raw table (not the final table itself) to hand
    // out-of-order record insertions after the delete has been registered
    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "final_table_id", stream.id().finalTableId(QUOTE, finalSuffix),
        "raw_table_id", stream.id().rawTableId(QUOTE),
        "pk_list", pkList,
        "pk_extracts", pkCasts,
        "quoted_cdc_delete_column", QUOTE + "_ab_cdc_deleted_at" + QUOTE)).replace(
            """
            DELETE FROM ${project_id}.${final_table_id}
            WHERE
              (${pk_list}) IN (
                SELECT (
                    ${pk_extracts}
                  )
                FROM  ${project_id}.${raw_table_id}
                WHERE JSON_TYPE(PARSE_JSON(JSON_QUERY(`_airbyte_data`, '$._ab_cdc_deleted_at'), wide_number_mode=>'round')) != 'null'
              )
            ;""");
  }

  @VisibleForTesting
  String dedupRawTable(final StreamId id, final String finalSuffix) {
    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "raw_table_id", id.rawTableId(QUOTE),
        "final_table_id", id.finalTableId(QUOTE, finalSuffix))).replace(
            // Note that this leaves _all_ deletion records in the raw table. We _could_ clear them out, but it
            // would be painful,
            // and it only matters in a few edge cases.
            """
            DELETE FROM
              ${project_id}.${raw_table_id}
            WHERE
              `_airbyte_raw_id` NOT IN (
                SELECT `_airbyte_raw_id` FROM ${project_id}.${final_table_id}
              )
            ;""");
  }

  @VisibleForTesting
  String commitRawTable(final StreamId id) {
    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "raw_table_id", id.rawTableId(QUOTE))).replace(
            """
            UPDATE ${project_id}.${raw_table_id}
            SET `_airbyte_loaded_at` = CURRENT_TIMESTAMP()
            WHERE `_airbyte_loaded_at` IS NULL
            ;""");
  }

  @Override
  public String overwriteFinalTable(final StreamId streamId, final String finalSuffix) {
    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "final_table_id", streamId.finalTableId(QUOTE),
        "tmp_final_table", streamId.finalTableId(QUOTE, finalSuffix),
        "real_final_table", streamId.finalName(QUOTE))).replace(
            """
            DROP TABLE IF EXISTS ${project_id}.${final_table_id};
            ALTER TABLE ${project_id}.${tmp_final_table} RENAME TO ${real_final_table};
            """);
  }

  private String wrapAndQuote(final String namespace, final String tableName) {
    return Stream.of(namespace, tableName)
        .map(part -> StringUtils.wrap(part, QUOTE))
        .collect(joining("."));
  }

  @Override
  public String migrateFromV1toV2(final StreamId streamId, final String namespace, final String tableName) {
    return new StringSubstitutor(Map.of(
        "project_id", '`' + projectId + '`',
        "raw_namespace", StringUtils.wrap(streamId.rawNamespace(), QUOTE),
        "dataset_location", datasetLocation,
        "v2_raw_table", streamId.rawTableId(QUOTE),
        "v1_raw_table", wrapAndQuote(namespace, tableName))).replace(
            """
            CREATE SCHEMA IF NOT EXISTS ${project_id}.${raw_namespace}
            OPTIONS(location="${dataset_location}");

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
            """);
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

  private static String cast(final String content, final String asType, boolean useSafeCast) {
    final var open = useSafeCast ? "SAFE_CAST(" : "CAST(";
    return wrap(open, content + " as " + asType, ")");
  }

  private static Set<String> getPks(StreamConfig stream) {
    return stream.primaryKey() != null ? stream.primaryKey().stream().map(ColumnId::name).collect(Collectors.toSet()) : Collections.emptySet();
  }

  private static String wrap(final String open, final String content, final String close) {
    return open + content + close;
  }

}
