/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static io.airbyte.integrations.base.destination.typing_deduping.Sql.concat;
import static io.airbyte.integrations.base.destination.typing_deduping.Sql.transactionally;
import static io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.SOFT_RESET_SUFFIX;
import static java.util.stream.Collectors.joining;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableList;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
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
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.text.StringSubstitutor;

public class SnowflakeSqlGenerator implements SqlGenerator {

  public static final String QUOTE = "\"";

  private final ColumnId CDC_DELETED_AT_COLUMN = buildColumnId("_ab_cdc_deleted_at");

  // See https://docs.snowflake.com/en/sql-reference/reserved-keywords.html
  // and
  // https://github.com/airbytehq/airbyte/blob/f226503bd1d4cd9c7412b04d47de584523988443/airbyte-integrations/bases/base-normalization/normalization/transform_catalog/reserved_keywords.py
  private static final List<String> RESERVED_COLUMN_NAMES = ImmutableList.of(
      "CURRENT_DATE",
      "CURRENT_TIME",
      "CURRENT_TIMESTAMP",
      "CURRENT_USER",
      "LOCALTIME",
      "LOCALTIMESTAMP");

  private final int retentionPeriodDays;

  public SnowflakeSqlGenerator(int retentionPeriodDays) {
    this.retentionPeriodDays = retentionPeriodDays;
  }

  @Override
  public StreamId buildStreamId(final String namespace, final String name, final String rawNamespaceOverride) {
    return new StreamId(
        escapeSqlIdentifier(namespace).toUpperCase(),
        escapeSqlIdentifier(name).toUpperCase(),
        escapeSqlIdentifier(rawNamespaceOverride),
        escapeSqlIdentifier(StreamId.concatenateRawTableName(namespace, name)),
        namespace,
        name);
  }

  @Override
  public ColumnId buildColumnId(final String name, final String suffix) {
    final String escapedName = prefixReservedColumnName(escapeSqlIdentifier(name).toUpperCase()) + suffix.toUpperCase();
    return new ColumnId(escapedName, name, escapedName);
  }

  public String toDialectType(final AirbyteType type) {
    if (type instanceof final AirbyteProtocolType p) {
      return toDialectType(p);
    } else if (type instanceof Struct) {
      // TODO should this+array just be VARIANT?
      return "OBJECT";
    } else if (type instanceof Array) {
      return "ARRAY";
    } else if (type instanceof UnsupportedOneOf) {
      return "VARIANT";
    } else if (type instanceof final Union u) {
      final AirbyteType typeWithPrecedence = u.chooseType();
      // typeWithPrecedence is never a Union, so this recursion is safe.
      return toDialectType(typeWithPrecedence);
    }

    // Literally impossible; AirbyteType is a sealed interface.
    throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
  }

  public String toDialectType(final AirbyteProtocolType airbyteProtocolType) {
    // TODO verify these types against normalization
    return switch (airbyteProtocolType) {
      case STRING -> "TEXT";
      case NUMBER -> "FLOAT";
      case INTEGER -> "NUMBER";
      case BOOLEAN -> "BOOLEAN";
      case TIMESTAMP_WITH_TIMEZONE -> "TIMESTAMP_TZ";
      case TIMESTAMP_WITHOUT_TIMEZONE -> "TIMESTAMP_NTZ";
      // If you change this - also change the logic in extractAndCast
      case TIME_WITH_TIMEZONE -> "TEXT";
      case TIME_WITHOUT_TIMEZONE -> "TIME";
      case DATE -> "DATE";
      case UNKNOWN -> "VARIANT";
    };
  }

  @Override
  public Sql createSchema(final String schema) {
    return Sql.of(new StringSubstitutor(Map.of("schema", StringUtils.wrap(schema, QUOTE)))
        .replace("CREATE SCHEMA IF NOT EXISTS ${schema};"));
  }

  @Override
  public Sql createTable(final StreamConfig stream, final String suffix, final boolean force) {
    final String columnDeclarations = stream.getColumns().entrySet().stream()
        .map(column -> "," + column.getKey().name(QUOTE) + " " + toDialectType(column.getValue()))
        .collect(joining("\n"));
    final String forceCreateTable = force ? "OR REPLACE" : "";

    return Sql.of(new StringSubstitutor(Map.of(
        "final_table_id", stream.getId().finalTableId(QUOTE, suffix.toUpperCase()),
        "force_create_table", forceCreateTable,
        "column_declarations", columnDeclarations,
        "retention_period_days", retentionPeriodDays)).replace(
            """
            CREATE ${force_create_table} TABLE ${final_table_id} (
              "_AIRBYTE_RAW_ID" TEXT NOT NULL,
              "_AIRBYTE_EXTRACTED_AT" TIMESTAMP_TZ NOT NULL,
              "_AIRBYTE_META" VARIANT NOT NULL
              ${column_declarations}
            ) data_retention_time_in_days = ${retention_period_days};
            """));
  }

  @Override
  public Sql updateTable(final StreamConfig stream,
                         final String finalSuffix,
                         final Optional<Instant> minRawTimestamp,
                         final boolean useExpensiveSaferCasting) {
    final String insertNewRecords = insertNewRecords(stream, finalSuffix, stream.getColumns(), minRawTimestamp, useExpensiveSaferCasting);
    String dedupFinalTable = "";
    String cdcDeletes = "";
    if (stream.getDestinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      dedupFinalTable = dedupFinalTable(stream.getId(), finalSuffix, stream.getPrimaryKey(), stream.getCursor());
      cdcDeletes = cdcDeletes(stream, finalSuffix);
    }
    final String commitRawTable = commitRawTable(stream.getId());

    return transactionally(insertNewRecords, dedupFinalTable, cdcDeletes, commitRawTable);
  }

  private String extractAndCast(final ColumnId column, final AirbyteType airbyteType, final boolean useTryCast) {
    return cast("\"_airbyte_data\":\"" + escapeJsonIdentifier(column.getOriginalName()) + "\"", airbyteType, useTryCast);
  }

  private String cast(final String sqlExpression, final AirbyteType airbyteType, final boolean useTryCast) {
    final String castMethod = useTryCast ? "TRY_CAST" : "CAST";
    if (airbyteType instanceof final Union u) {
      // This is guaranteed to not be a Union, so we won't recurse infinitely
      final AirbyteType chosenType = u.chooseType();
      return cast(sqlExpression, chosenType, useTryCast);
    } else if (airbyteType == AirbyteProtocolType.TIME_WITH_TIMEZONE) {
      // We're using TEXT for this type, so need to explicitly check the string format.
      // There's a bunch of ways we could do this; this regex is approximately correct and easy to
      // implement.
      // It'll match anything like HH:MM:SS[.SSS](Z|[+-]HH[:]MM), e.g.:
      // 12:34:56Z
      // 12:34:56.7+08:00
      // 12:34:56.7890123-0800
      // 12:34:56-08
      return new StringSubstitutor(Map.of("expression", sqlExpression)).replace(
          """
          CASE
            WHEN NOT ((${expression})::TEXT REGEXP '\\\\d{1,2}:\\\\d{2}:\\\\d{2}(\\\\.\\\\d+)?(Z|[+\\\\-]\\\\d{1,2}(:?\\\\d{2})?)')
              THEN NULL
            ELSE ${expression}
          END
          """);
    } else {
      final String dialectType = toDialectType(airbyteType);
      return switch (dialectType) {
        case "TIMESTAMP_TZ" -> new StringSubstitutor(Map.of("expression", sqlExpression, "cast", castMethod)).replace(
            // Handle offsets in +/-HHMM and +/-HH formats
            // The four cases, in order, match:
            // 2023-01-01T12:34:56-0800
            // 2023-01-01T12:34:56-08
            // 2023-01-01T12:34:56.7890123-0800
            // 2023-01-01T12:34:56.7890123-08
            // And the ELSE will try to handle everything else.
            """
            CASE
              WHEN (${expression})::TEXT REGEXP '\\\\d{4}-\\\\d{2}-\\\\d{2}T(\\\\d{2}:){2}\\\\d{2}(\\\\+|-)\\\\d{4}'
                THEN TO_TIMESTAMP_TZ((${expression})::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZHTZM')
              WHEN (${expression})::TEXT REGEXP '\\\\d{4}-\\\\d{2}-\\\\d{2}T(\\\\d{2}:){2}\\\\d{2}(\\\\+|-)\\\\d{2}'
                THEN TO_TIMESTAMP_TZ((${expression})::TEXT, 'YYYY-MM-DDTHH24:MI:SSTZH')
              WHEN (${expression})::TEXT REGEXP '\\\\d{4}-\\\\d{2}-\\\\d{2}T(\\\\d{2}:){2}\\\\d{2}\\\\.\\\\d{1,7}(\\\\+|-)\\\\d{4}'
                THEN TO_TIMESTAMP_TZ((${expression})::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZHTZM')
              WHEN (${expression})::TEXT REGEXP '\\\\d{4}-\\\\d{2}-\\\\d{2}T(\\\\d{2}:){2}\\\\d{2}\\\\.\\\\d{1,7}(\\\\+|-)\\\\d{2}'
                THEN TO_TIMESTAMP_TZ((${expression})::TEXT, 'YYYY-MM-DDTHH24:MI:SS.FFTZH')
              ELSE ${cast}((${expression})::TEXT AS TIMESTAMP_TZ)
            END
            """);
        // try_cast doesn't support variant/array/object, so handle them specially
        case "VARIANT" -> sqlExpression;
        // We need to validate that the struct is actually a struct.
        // Note that struct columns are actually nullable in two ways. For a column `foo`:
        // {foo: null} and {} are both valid, and are both written to the final table as a SQL NULL (_not_ a
        // JSON null).
        case "OBJECT" -> new StringSubstitutor(Map.of("expression", sqlExpression)).replace(
            """
            CASE
              WHEN TYPEOF(${expression}) != 'OBJECT'
                THEN NULL
              ELSE ${expression}
            END
            """);
        // Much like the object case, arrays need special handling.
        case "ARRAY" -> new StringSubstitutor(Map.of("expression", sqlExpression)).replace(
            """
            CASE
              WHEN TYPEOF(${expression}) != 'ARRAY'
                THEN NULL
              ELSE ${expression}
            END
            """);
        case "TEXT" -> "((" + sqlExpression + ")::text)"; // we don't need TRY_CAST on strings.
        default -> castMethod + "((" + sqlExpression + ")::text as " + dialectType + ")";
      };
    }
  }

  private static String airbyteExtractedAtUtcForced(final String sqlExpression) {
    return new StringSubstitutor(Map.of("expression", sqlExpression)).replace(
        """
        TIMESTAMPADD(
          HOUR,
          EXTRACT(timezone_hour from ${expression}),
          TIMESTAMPADD(
            MINUTE,
            EXTRACT(timezone_minute from ${expression}),
            CONVERT_TIMEZONE('UTC', ${expression})
          )
        )
        """);
  }

  @VisibleForTesting
  String insertNewRecords(final StreamConfig stream,
                          final String finalSuffix,
                          final LinkedHashMap<ColumnId, AirbyteType> streamColumns,
                          final Optional<Instant> minRawTimestamp,
                          final boolean useTryCast) {
    final String columnList = streamColumns.keySet().stream().map(quotedColumnId -> quotedColumnId.name(QUOTE) + ",").collect(joining("\n"));
    final String extractNewRawRecords = extractNewRawRecords(stream, minRawTimestamp, useTryCast);

    return new StringSubstitutor(Map.of(
        "final_table_id", stream.getId().finalTableId(QUOTE, finalSuffix.toUpperCase()),
        "column_list", columnList,
        "extractNewRawRecords", extractNewRawRecords)).replace(
            """
            INSERT INTO ${final_table_id}
            (
            ${column_list}
              "_AIRBYTE_META",
              "_AIRBYTE_RAW_ID",
              "_AIRBYTE_EXTRACTED_AT"
            )
            ${extractNewRawRecords};""");
  }

  private String extractNewRawRecords(final StreamConfig stream, final Optional<Instant> minRawTimestamp, final boolean useTryCast) {
    final String columnCasts = stream.getColumns().entrySet().stream().map(
        col -> extractAndCast(col.getKey(), col.getValue(), useTryCast) + " as " + col.getKey().name(QUOTE) + ",")
        .collect(joining("\n"));
    final String columnErrors = stream.getColumns().entrySet().stream().map(
        col -> new StringSubstitutor(Map.of(
            "raw_col_name", escapeJsonIdentifier(col.getKey().getOriginalName()),
            "printable_col_name", escapeSingleQuotedString(col.getKey().getOriginalName()),
            "col_type", toDialectType(col.getValue()),
            "json_extract", extractAndCast(col.getKey(), col.getValue(), useTryCast))).replace(
                // TYPEOF returns "NULL_VALUE" for a JSON null and "NULL" for a SQL null
                """
                CASE
                  WHEN (TYPEOF("_airbyte_data":"${raw_col_name}") NOT IN ('NULL', 'NULL_VALUE'))
                    AND (${json_extract} IS NULL)
                    THEN 'Problem with `${printable_col_name}`'
                  ELSE NULL
                END"""))
        .collect(joining(",\n"));
    final String columnList = stream.getColumns().keySet().stream().map(quotedColumnId -> quotedColumnId.name(QUOTE) + ",").collect(joining("\n"));
    final String extractedAtCondition = buildExtractedAtCondition(minRawTimestamp);

    if (stream.getDestinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      String cdcConditionalOrIncludeStatement = "";
      if (stream.getColumns().containsKey(CDC_DELETED_AT_COLUMN)) {
        cdcConditionalOrIncludeStatement = """
                                           OR (
                                             "_airbyte_loaded_at" IS NOT NULL
                                             AND TYPEOF("_airbyte_data":"_ab_cdc_deleted_at") NOT IN ('NULL', 'NULL_VALUE')
                                           )
                                           """;
      }

      final String pkList = stream.getPrimaryKey().stream().map(columnId -> columnId.name(QUOTE)).collect(joining(","));
      final String cursorOrderClause = stream.getCursor()
          .map(cursorId -> cursorId.name(QUOTE) + " DESC NULLS LAST,")
          .orElse("");

      return new StringSubstitutor(Map.of(
          "raw_table_id", stream.getId().rawTableId(QUOTE),
          "column_casts", columnCasts,
          "column_errors", columnErrors,
          "cdcConditionalOrIncludeStatement", cdcConditionalOrIncludeStatement,
          "extractedAtCondition", extractedAtCondition,
          "column_list", columnList,
          "pk_list", pkList,
          "cursor_order_clause", cursorOrderClause,
          "airbyte_extracted_at_utc", airbyteExtractedAtUtcForced("\"_airbyte_extracted_at\""))).replace(
              """
              WITH intermediate_data AS (
                SELECT
              ${column_casts}
              ARRAY_CONSTRUCT_COMPACT(${column_errors}) as "_airbyte_cast_errors",
                "_airbyte_raw_id",
                ${airbyte_extracted_at_utc} as "_airbyte_extracted_at"
                FROM ${raw_table_id}
                WHERE (
                    "_airbyte_loaded_at" IS NULL
                    ${cdcConditionalOrIncludeStatement}
                  ) ${extractedAtCondition}
              ), new_records AS (
                SELECT
                ${column_list}
                  OBJECT_CONSTRUCT('errors', "_airbyte_cast_errors") AS "_AIRBYTE_META",
                  "_airbyte_raw_id" AS "_AIRBYTE_RAW_ID",
                  "_airbyte_extracted_at" AS "_AIRBYTE_EXTRACTED_AT"
                FROM intermediate_data
              ), numbered_rows AS (
                SELECT *, row_number() OVER (
                  PARTITION BY ${pk_list} ORDER BY ${cursor_order_clause} "_AIRBYTE_EXTRACTED_AT" DESC
                ) AS row_number
                FROM new_records
              )
              SELECT ${column_list} "_AIRBYTE_META", "_AIRBYTE_RAW_ID", "_AIRBYTE_EXTRACTED_AT"
              FROM numbered_rows
              WHERE row_number = 1""");
    } else {
      return new StringSubstitutor(Map.of(
          "raw_table_id", stream.getId().rawTableId(QUOTE),
          "column_casts", columnCasts,
          "column_errors", columnErrors,
          "extractedAtCondition", extractedAtCondition,
          "column_list", columnList,
          "airbyte_extracted_at_utc", airbyteExtractedAtUtcForced("\"_airbyte_extracted_at\""))).replace(
              """
              WITH intermediate_data AS (
                SELECT
              ${column_casts}
              ARRAY_CONSTRUCT_COMPACT(${column_errors}) as "_airbyte_cast_errors",
                "_airbyte_raw_id",
                ${airbyte_extracted_at_utc} as "_airbyte_extracted_at"
                FROM ${raw_table_id}
                WHERE
                  "_airbyte_loaded_at" IS NULL
                  ${extractedAtCondition}
              )
              SELECT
              ${column_list}
                OBJECT_CONSTRUCT('errors', "_airbyte_cast_errors") AS "_AIRBYTE_META",
                "_airbyte_raw_id" AS "_AIRBYTE_RAW_ID",
                "_airbyte_extracted_at" AS "_AIRBYTE_EXTRACTED_AT"
              FROM intermediate_data""");
    }
  }

  private static String buildExtractedAtCondition(final Optional<Instant> minRawTimestamp) {
    return minRawTimestamp
        .map(ts -> " AND " + airbyteExtractedAtUtcForced("\"_airbyte_extracted_at\"") + " > '" + ts + "'")
        .orElse("");
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
        "final_table_id", id.finalTableId(QUOTE, finalSuffix.toUpperCase()),
        "pk_list", pkList,
        "cursor_order_clause", cursorOrderClause,
        "airbyte_extracted_at_utc", airbyteExtractedAtUtcForced("\"_AIRBYTE_EXTRACTED_AT\""))).replace(
            """
            DELETE FROM ${final_table_id}
            WHERE "_AIRBYTE_RAW_ID" IN (
              SELECT "_AIRBYTE_RAW_ID" FROM (
                SELECT "_AIRBYTE_RAW_ID", row_number() OVER (
                  PARTITION BY ${pk_list} ORDER BY ${cursor_order_clause} ${airbyte_extracted_at_utc} DESC
                ) as row_number FROM ${final_table_id}
              )
              WHERE row_number != 1
            );
            """);
  }

  private String cdcDeletes(final StreamConfig stream, final String finalSuffix) {
    if (stream.getDestinationSyncMode() != DestinationSyncMode.APPEND_DEDUP) {
      return "";
    }
    if (!stream.getColumns().containsKey(CDC_DELETED_AT_COLUMN)) {
      return "";
    }

    // we want to grab IDs for deletion from the raw table (not the final table itself) to hand
    // out-of-order record insertions after the delete has been registered
    return new StringSubstitutor(Map.of(
        "final_table_id", stream.getId().finalTableId(QUOTE, finalSuffix.toUpperCase()))).replace(
            """
            DELETE FROM ${final_table_id}
            WHERE _AB_CDC_DELETED_AT IS NOT NULL;
            """);
  }

  @VisibleForTesting
  String commitRawTable(final StreamId id) {
    return new StringSubstitutor(Map.of(
        "raw_table_id", id.rawTableId(QUOTE))).replace(
            """
            UPDATE ${raw_table_id}
            SET "_airbyte_loaded_at" = CURRENT_TIMESTAMP()
            WHERE "_airbyte_loaded_at" IS NULL
            ;""");
  }

  @Override
  public Sql overwriteFinalTable(final StreamId stream, final String finalSuffix) {
    final StringSubstitutor substitutor = new StringSubstitutor(Map.of(
        "final_table", stream.finalTableId(QUOTE),
        "tmp_final_table", stream.finalTableId(QUOTE, finalSuffix.toUpperCase())));
    return transactionally(
        substitutor.replace("DROP TABLE IF EXISTS ${final_table};"),
        substitutor.replace("ALTER TABLE ${tmp_final_table} RENAME TO ${final_table};"));
  }

  @Override
  public Sql prepareTablesForSoftReset(final StreamConfig stream) {
    return concat(
        createTable(stream, SOFT_RESET_SUFFIX.toUpperCase(), true),
        clearLoadedAt(stream.getId()));
  }

  @Override
  public Sql clearLoadedAt(final StreamId streamId) {
    return Sql.of(new StringSubstitutor(Map.of("raw_table_id", streamId.rawTableId(QUOTE)))
        .replace("""
                 UPDATE ${raw_table_id} SET "_airbyte_loaded_at" = NULL;
                 """));
  }

  @Override
  public Sql migrateFromV1toV2(final StreamId streamId, final String namespace, final String tableName) {
    // In the SQL below, the v2 values are quoted to preserve their case while the v1 values are
    // intentionally _not_ quoted. This is to preserve the implicit upper-casing behavior in v1.
    return Sql.of(new StringSubstitutor(Map.of(
        "raw_table_name", streamId.rawTableId(QUOTE),
        "raw_id", JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
        "extracted_at", JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
        "loaded_at", JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
        "data", JavaBaseConstants.COLUMN_NAME_DATA,
        "v1_raw_id", JavaBaseConstants.COLUMN_NAME_AB_ID,
        "emitted_at", JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
        "v1_raw_table", String.join(".", namespace, tableName)))
            .replace(
                """
                CREATE OR REPLACE TABLE ${raw_table_name} (
                  "${raw_id}" VARCHAR PRIMARY KEY,
                  "${extracted_at}" TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp(),
                  "${loaded_at}" TIMESTAMP WITH TIME ZONE DEFAULT NULL,
                  "${data}" VARIANT
                )
                data_retention_time_in_days = 0
                AS (
                  SELECT
                    ${v1_raw_id} AS "${raw_id}",
                    ${emitted_at} AS "${extracted_at}",
                    CAST(NULL AS TIMESTAMP WITH TIME ZONE) AS "${loaded_at}",
                    PARSE_JSON(${data}) AS "${data}"
                  FROM ${v1_raw_table}
                )
                ;
                """));
  }

  /**
   * Snowflake json object access is done using double-quoted strings, e.g. `SELECT
   * "_airbyte_data":"foo"`. As such, we need to escape double-quotes in the field name.
   */
  public static String escapeJsonIdentifier(final String identifier) {
    // Note that we don't need to escape backslashes here!
    // The only special character in an identifier is the double-quote, which needs to be doubled.
    return identifier.replace("\"", "\"\"");
  }

  /**
   * SQL identifiers are also double-quoted strings. They have slightly more stringent requirements
   * than JSON field identifiers.
   * <p>
   * This method is separate from {@link #escapeJsonIdentifier(String)} because we need to retain the
   * original field name for JSON access, e.g. `SELECT "_airbyte_data":"${FOO" AS "__FOO"`.
   */
  public static String escapeSqlIdentifier(String identifier) {
    // Snowflake scripting language does something weird when the `${` bigram shows up in the script
    // so replace these with something else.
    // For completeness, if we trigger this, also replace closing curly braces with underscores.
    if (identifier.contains("${")) {
      identifier = identifier
          .replace("$", "_")
          .replace("{", "_")
          .replace("}", "_");
    }

    return escapeJsonIdentifier(identifier);
  }

  private static String prefixReservedColumnName(final String columnName) {
    return RESERVED_COLUMN_NAMES.stream().anyMatch(k -> k.equalsIgnoreCase(columnName)) ? "_" + columnName : columnName;
  }

  public static String escapeSingleQuotedString(final String str) {
    return str
        .replace("\\", "\\\\")
        .replace("'", "\\'");
  }

}
