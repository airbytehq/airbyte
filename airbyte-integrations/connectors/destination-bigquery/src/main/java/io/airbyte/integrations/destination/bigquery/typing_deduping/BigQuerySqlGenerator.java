package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static java.util.stream.Collectors.joining;

import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableDefinition;
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Object;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Primitive;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.UnsupportedOneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.StreamConfig;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.Map;
import java.util.stream.Collectors;
import org.apache.commons.text.StringSubstitutor;

public class BigQuerySqlGenerator implements SqlGenerator<TableDefinition, StandardSQLTypeName> {

  private static final BigQuerySQLNameTransformer nameTransformer = new BigQuerySQLNameTransformer();

  // metadata columns
  private final String RAW_ID = quoteColumnId("_airbyte_raw_id").name();


  // hardcoded CDC column name for deletions
  private final QuotedColumnId DELETED_AT = quoteColumnId("_ab_cdc_deleted_at");

  @Override
  public QuotedStreamId quoteStreamId(final String namespace, final String name) {
    return new QuotedStreamId(
        // TODO is this correct?
        nameTransformer.getNamespace(namespace),
        nameTransformer.convertStreamName(name),
        // TODO constant
        nameTransformer.getNamespace("airbyte"),
        // TODO maybe do something with #getRawTableName?
        nameTransformer.convertStreamName(namespace + "_" + name),
        namespace,
        name);
  }

  @Override
  public QuotedColumnId quoteColumnId(final String name) {
    // TODO this is probably wrong
    return new QuotedColumnId(nameTransformer.getIdentifier(name), name);
  }

  @Override
  public StandardSQLTypeName toDialectType(final AirbyteType type) {
    // switch pattern-matching is still in preview at language level 17 :(
    if (type instanceof final Primitive p) {
      return toDialectType(p);
    } else if (type instanceof final Object o) {
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      return StandardSQLTypeName.STRING;
    } else if (type instanceof final Array a) {
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      return StandardSQLTypeName.STRING;
    } else if (type instanceof final UnsupportedOneOf u) {
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      return StandardSQLTypeName.STRING;
    } else if (type instanceof final OneOf o) {
      // TODO choose the best data type + map to bigquery type
      return null;
    }

    // Literally impossible; AirbyteType is a sealed interface.
    throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
  }

  public StandardSQLTypeName toDialectType(final Primitive primitive) {
    // TODO maybe this should be in the interface? unclear if that has value, but I expect every implementation to have this method
    return switch (primitive) {
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
        .map(column -> column.getKey().name() + " " + column.getValue().name())
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
    String pkNullChecks = stream.primaryKey().stream().map(
        pk -> "AND SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$." + pk.originalName() + "') as " + stream.columns().get(pk).name() + ") IS NULL"
    ).collect(joining("\n"));
    // TODO - this needs the original AirbyteType so that we can recognize which columns need JSON_QUERY vs JSON_VALUE
    String columnCasts = stream.columns().entrySet().stream().map(
        col -> "SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$." + col.getKey().originalName() + "') as " + col.getValue().name() + ") as " + col.getKey()
            .name() + ","
    ).collect(joining("\n"));
    String columnErrors = stream.columns().entrySet().stream().map(
        col -> new StringSubstitutor(Map.of(
          "raw_col_name", col.getKey().originalName(),
            "col_type", col.getValue().name()
        )).replace(
            """
                CASE
                  WHEN (JSON_VALUE(`_airbyte_data`, '$.${raw_col_name}') IS NOT NULL) AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$.${raw_col_name}') as ${col_type}) IS NULL) THEN ["Problem with `${raw_col_name}`"]
                  ELSE []
                END"""
        )
    ).collect(joining(",\n"));
    String pkList = stream.primaryKey().stream().map(QuotedColumnId::name).collect(joining(","));
    // TODO - this needs the original AirbyteType so that we can recognize which columns need JSON_QUERY vs JSON_VALUE
    String pkEqualityChecks = stream.columns().entrySet().stream()
        .filter(e -> stream.primaryKey().contains(e.getKey()))
        .map(
        col -> new StringSubstitutor(Map.of(
            "raw_col_name", col.getKey().originalName(),
            "col_type", col.getValue().name()
        )).replace("""
            `id` IN (
              SELECT
                SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$.${raw_col_name}') as ${col_type}) as id
              FROM ${raw_table_id}
              WHERE JSON_VALUE(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NOT NULL
            )""")
    ).collect(joining("\nAND "));

    return new StringSubstitutor(Map.of(
        "raw_table_id", stream.id().rawTableId(),
        // TODO handle final suffix
        "final_table_id", stream.id().finalTableId(),
        "pk_null_checks", pkNullChecks,
        "column_casts", columnCasts,
        "column_errors", columnErrors,
        "pk_list", pkList,
        "pk_equality_checks", pkEqualityChecks
    )).replace(
        """
            DECLARE missing_pk_count INT64;
                        
            BEGIN TRANSACTION;
              -- Step 1: Validate the incoming data
              SET missing_pk_count = (
                SELECT COUNT(1)
                FROM ${raw_table_id}
                WHERE
                  `_airbyte_loaded_at` IS NULL
                  ${pk_null_checks}
                );
                      
              IF missing_pk_count > 0 THEN
                RAISE USING message = FORMAT("Raw table has %s rows missing a primary key", CAST(missing_pk_count AS STRING));
              END IF;
                      
              -- Step 2: Move the new data to the typed table
              INSERT INTO ${final_table_id}
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
              ;
                      
              -- Step 3: Dedupe and clean the typed table
              DELETE FROM testing_evan_2052.users
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
            ${pk_equality_checks}
                )
              ;
                      
              -- Step 4: Remove old entries from Raw table
              DELETE FROM
                ${raw_table_id}
              WHERE
                `_airbyte_raw_id` NOT IN (
                  SELECT `_airbyte_raw_id` FROM ${final_table_id}
                )
                AND
                JSON_VALUE(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NULL
              ;
                      
              -- Step 5: Apply typed_at timestamp where needed
              UPDATE ${raw_table_id}
              SET `_airbyte_loaded_at` = CURRENT_TIMESTAMP()
              WHERE `_airbyte_loaded_at` IS NULL
              ;
                      
            COMMIT TRANSACTION;
            """
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
