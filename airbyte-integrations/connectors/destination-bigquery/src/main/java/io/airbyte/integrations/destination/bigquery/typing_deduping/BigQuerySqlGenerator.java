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
import org.apache.commons.text.StringSubstitutor;

public class BigQuerySqlGenerator implements SqlGenerator<TableDefinition, StandardSQLTypeName> {

  private static final BigQuerySQLNameTransformer nameTransformer = new BigQuerySQLNameTransformer();

  // metadata columns
  private final String RAW_ID = quoteColumnId("_airbyte_raw_id").name();

  @Override
  public QuotedStreamId quoteStreamId(final String namespace, final String name) {
    return new QuotedStreamId(
        // TODO is this correct?
        nameTransformer.getNamespace(namespace),
        nameTransformer.convertStreamName(name),
        // TODO constant
        nameTransformer.getNamespace("airbyte"),
        // TODO maybe do something with #getRawTableName?
        nameTransformer.convertStreamName(namespace + "_" + name));
  }

  @Override
  public QuotedColumnId quoteColumnId(final String name) {
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
    return new QuotedColumnId(nameTransformer.getIdentifier(quotedName), name, canonicalized);
  }

  @Override
  public ParsedType<StandardSQLTypeName> toDialectType(final AirbyteType type) {
    // switch pattern-matching is still in preview at language level 17 :(
    if (type instanceof final AirbyteProtocolType p) {
      return new ParsedType<>(toDialectType(p), type);
    } else if (type instanceof final Struct o) {
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      return new ParsedType<>(StandardSQLTypeName.STRING, type);
    } else if (type instanceof final Array a) {
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      return new ParsedType<>(StandardSQLTypeName.STRING, type);
    } else if (type instanceof final UnsupportedOneOf u) {
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      return new ParsedType<>(StandardSQLTypeName.STRING, type);
    } else if (type instanceof final OneOf o) {
      // TODO choose the best data type + map to bigquery type
      return null;
    }

    // Literally impossible; AirbyteType is a sealed interface.
    throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
  }

  private String extractAndCast(QuotedColumnId column, AirbyteType airbyteType, StandardSQLTypeName dialectType) {
    // TODO also handle oneOf types
    if (airbyteType instanceof Struct || airbyteType instanceof Array || airbyteType instanceof UnsupportedOneOf || airbyteType == AirbyteProtocolType.UNKNOWN) {
      // TODO handle null better (don't stringify it)
      return "TO_JSON_STRING(JSON_QUERY(`_airbyte_data`, '$." + column.originalName() + "'))";
    } else {
      return "SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$." + column.originalName() + "') as " + dialectType.name() + ")";
    }
  }

  public StandardSQLTypeName toDialectType(final AirbyteProtocolType airbyteProtocolType) {
    // TODO maybe this should be in the interface? unclear if that has value, but I expect every implementation to have this method
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
  public String createTable(final StreamConfig<StandardSQLTypeName> stream) {
    final String columnDeclarations = stream.columns().entrySet().stream()
        .map(column -> column.getKey().name() + " " + column.getValue().dialectType().name())
        .collect(joining(",\n"));
    final String clusterConfig;
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      // We're doing deduping, therefore we have a primary key.
      // Cluster on all the PK columns, and also extracted_at.
      clusterConfig = stream.primaryKey().stream().map(QuotedColumnId::name).collect(joining(",")) + ", _airbyte_extracted_at";
    } else {
      // Otherwise just cluser on extracted_at.
      clusterConfig = "_airbyte_extracted_at";
    }

    return new StringSubstitutor(Map.of(
        "final_table_id", stream.id().finalTableId(),
        "column_declarations", columnDeclarations,
        "cluster_config", clusterConfig
    )).replace("""
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
    return null;
  }

  @Override
  public String updateTable(final String finalSuffix, final StreamConfig<StandardSQLTypeName> stream) {
    // TODO this method needs to handle all the sync modes
    // e.g. this pk null check should only happen for incremental dedup

    String validatePrimaryKeys = validatePrimaryKeys(stream.id(), stream.primaryKey(), stream.columns());
    String insertNewRecords = insertNewRecords(stream.id(), stream.columns());
    String dedupFinalTable = dedupFinalTable(stream.id(), stream.primaryKey(), stream.columns());
    String dedupRawTable = dedupRawTable(stream.id());
    String commitRawTable = commitRawTable(stream.id());

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
  String validatePrimaryKeys(QuotedStreamId id, List<QuotedColumnId> primaryKeys, LinkedHashMap<QuotedColumnId, ParsedType<StandardSQLTypeName>> streamColumns) {
    // TODO this method needs to handle all the sync modes
    // e.g. this pk null check should only happen for incremental dedup
    String pkNullChecks = primaryKeys.stream().map(
        pk -> {
          String jsonExtract = extractAndCast(pk, streamColumns.get(pk).airbyteType(), streamColumns.get(pk).dialectType());
          return "AND " + jsonExtract + " IS NULL";
        }
    ).collect(joining("\n"));

    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(),
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
  String insertNewRecords(final QuotedStreamId id, final LinkedHashMap<QuotedColumnId, ParsedType<StandardSQLTypeName>> streamColumns) {
    String columnCasts = streamColumns.entrySet().stream().map(
        col -> extractAndCast(col.getKey(), col.getValue().airbyteType(), col.getValue().dialectType()) + " as " + col.getKey().name() + ","
    ).collect(joining("\n"));
    String columnErrors = streamColumns.entrySet().stream().map(
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
    String columnList = streamColumns.keySet().stream().map(quotedColumnId -> quotedColumnId.name() + ",").collect(joining("\n"));

    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(),
        "final_table_id", id.finalTableId(),
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
  String dedupFinalTable(QuotedStreamId id, final List<QuotedColumnId> primaryKey, final LinkedHashMap<QuotedColumnId, ParsedType<StandardSQLTypeName>> streamColumns) {
    String pkList = primaryKey.stream().map(QuotedColumnId::name).collect(joining(","));
    String pkCastList = streamColumns.entrySet().stream()
        .filter(e -> primaryKey.contains(e.getKey()))
        .map(e -> extractAndCast(e.getKey(), e.getValue().airbyteType(), e.getValue().dialectType()))
        .collect(joining(",\n "));

    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(),
        "final_table_id", id.finalTableId(),
        "pk_list", pkList,
        "pk_cast_list", pkCastList
    )).replace(
        """
            DELETE FROM ${final_table_id}
            WHERE
              `_airbyte_raw_id` IN (
                SELECT `_airbyte_raw_id` FROM (
                  SELECT `_airbyte_raw_id`, row_number() OVER (
                    PARTITION BY ${pk_list} ORDER BY `updated_at` DESC, `_airbyte_extracted_at` DESC
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
  String dedupRawTable(final QuotedStreamId id) {
    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(),
        "final_table_id", id.finalTableId()
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
  String commitRawTable(final QuotedStreamId id) {
    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId()
    )).replace(
        """
              UPDATE ${raw_table_id}
              SET `_airbyte_loaded_at` = CURRENT_TIMESTAMP()
              WHERE `_airbyte_loaded_at` IS NULL
              ;"""
    );
  }

  @Override
  public String deleteOldRawRecords(final StreamConfig<StandardSQLTypeName> stream) {
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      // TODO maybe this should have an extracted_at / loaded_at condition for efficiency
      // We don't need to filter out `_airbyte_data ->> '_ab_cdc_deleted_at' IS NULL` because we can run this sql before executing CDC deletes
      return new StringSubstitutor(Map.of(
          "raw_table_id", stream.id().rawTableId(),
          "airbyte_raw_id", RAW_ID,
          "final_table_id", stream.id().finalTableId()
      )).replace("""
          DELETE FROM ${raw_table_id} WHERE ${airbyte_raw_id} NOT IN (
            SELECT ${airbyte_raw_id} FROM ${final_table_id}
          )
          """);
    } else {
      return "";
    }
  }

  @Override
  public String overwriteFinalTable(final String finalSuffix, final StreamConfig<StandardSQLTypeName> stream) {
    if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE && finalSuffix.length() > 0) {
      return new StringSubstitutor(Map.of(
          "final_table_id", stream.id().finalTableId(),
          "raw_table_id", stream.id().rawTableId() + "_" + finalSuffix,
          "final_table_name", stream.id().finalName()
      )).replace("""
          DROP TABLE ${final_table_id};
          ALTER TABLE ${raw_table_id} RENAME TO ${final_table_name};
          """);
    } else {
      return "";
    }
  }
}
