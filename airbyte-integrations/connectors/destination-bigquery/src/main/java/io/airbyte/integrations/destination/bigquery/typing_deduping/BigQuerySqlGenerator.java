package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static java.util.stream.Collectors.joining;

import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableDefinition;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Struct;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.OneOf;
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

  // metadata columns
  private final String RAW_ID = buildColumnId("_airbyte_raw_id").name(QUOTE);

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
    } else if (type instanceof final Struct s) {
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      return new ParsedType<>(StandardSQLTypeName.STRING, type);
    } else if (type instanceof final Array a) {
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      return new ParsedType<>(StandardSQLTypeName.STRING, type);
    } else if (type instanceof final UnsupportedOneOf u) {
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      return new ParsedType<>(StandardSQLTypeName.STRING, type);
    } else if (type instanceof final OneOf o) {
      final AirbyteType typeWithPrecedence = AirbyteTypeUtils.chooseOneOfType(o);
      final StandardSQLTypeName dialectType;
      if ((typeWithPrecedence instanceof Struct) || (typeWithPrecedence instanceof Array)) {
        dialectType = StandardSQLTypeName.STRING;
      } else {
        dialectType = toDialectType((AirbyteProtocolType) typeWithPrecedence);
      }
      return new ParsedType<>(dialectType, typeWithPrecedence);
    }

    // Literally impossible; AirbyteType is a sealed interface.
    throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
  }

  private String extractAndCast(final ColumnId column, final AirbyteType airbyteType, final StandardSQLTypeName dialectType) {
    // TODO also handle oneOf types
    if (airbyteType instanceof Struct || airbyteType instanceof Array || airbyteType instanceof UnsupportedOneOf || airbyteType == AirbyteProtocolType.UNKNOWN) {
      // TODO handle null better (don't stringify it)
      return "TO_JSON_STRING(JSON_QUERY(`_airbyte_data`, '$." + column.originalName() + "'))";
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
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      case UNKNOWN -> StandardSQLTypeName.STRING;
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
      dedupRawTable = dedupRawTable(stream.id(), finalSuffix);
      dedupFinalTable = dedupFinalTable(stream.id(), finalSuffix, stream.primaryKey(), stream.cursor(), stream.columns());
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

    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE),
        "final_table_id", id.finalTableId(finalSuffix, QUOTE),
        "column_casts", columnCasts,
        "column_errors", columnErrors,
        "column_list", columnList
    )).replace(
        // TODO if column_errors is an empty array, then set airbyte_meta to just {} (or at least {errors:null})
        """
              INSERT INTO ${final_table_id}
              (
            ${column_list}
            _airbyte_meta,
            _airbyte_raw_id,
            _airbyte_extracted_at
              )
              SELECT
            ${column_casts}
            to_json(struct(array_concat(
            ${column_errors}
            ) as errors)) as _airbyte_meta,
                _airbyte_raw_id,
                _airbyte_extracted_at
              FROM ${raw_table_id}
              WHERE
                _airbyte_loaded_at IS NULL
                AND JSON_EXTRACT(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NULL
              ;"""
    );
  }

  @VisibleForTesting
  String dedupFinalTable(final StreamId id, final String finalSuffix, final List<ColumnId> primaryKey, final Optional<ColumnId> cursor, final LinkedHashMap<ColumnId, ParsedType<StandardSQLTypeName>> streamColumns) {
    final String pkList = primaryKey.stream().map(columnId -> columnId.name(QUOTE)).collect(joining(","));
    final String pkCastList = streamColumns.entrySet().stream()
        .filter(e -> primaryKey.contains(e.getKey()))
        .map(e -> extractAndCast(e.getKey(), e.getValue().airbyteType(), e.getValue().dialectType()))
        .collect(joining(",\n "));
    final String cursorOrdering = cursor.map(quotedColumnId -> quotedColumnId.name(QUOTE) + " DESC,").orElse("");

    // TODO can the CDC deletes just use the final table deleted_at column? (this would allow us to delete deleted records from the raw table also)
    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE),
        "final_table_id", id.finalTableId(finalSuffix, QUOTE),
        "pk_list", pkList,
        "pk_cast_list", pkCastList,
        "cursor_ordering", cursorOrdering
    )).replace(
        """
            DELETE FROM ${final_table_id}
            WHERE
              `_airbyte_raw_id` IN (
                SELECT `_airbyte_raw_id` FROM (
                  SELECT `_airbyte_raw_id`, row_number() OVER (
                    PARTITION BY ${pk_list} ORDER BY ${cursor_ordering} `_airbyte_extracted_at` DESC
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
                  WHERE JSON_VALUE(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NOT NULL
                )
              )
            ;"""
    );
  }

  @VisibleForTesting
  String dedupRawTable(final StreamId id, final String finalSuffix) {
    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE),
        "final_table_id", id.finalTableId(finalSuffix, QUOTE)
    )).replace(
        // TODO remove the deleted_at clause if we don't have the cdc columns
        """
              DELETE FROM
                ${raw_table_id}
              WHERE
                `_airbyte_raw_id` NOT IN (
                  SELECT `_airbyte_raw_id` FROM ${final_table_id}
                )
                AND
                JSON_VALUE(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NULL
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
