package io.airbyte.integrations.destination.bigquery.typing_deduping;

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
import java.util.UUID;

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
    if (type instanceof Primitive p) {
      return toDialectType(p);
    } else if (type instanceof Object o) {
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      return StandardSQLTypeName.STRING;
    } else if (type instanceof Array a) {
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      return StandardSQLTypeName.STRING;
    } else if (type instanceof UnsupportedOneOf u) {
      // eventually this should be JSON; keep STRING for now as legacy compatibility
      return StandardSQLTypeName.STRING;
    } else if (type instanceof OneOf o) {
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
    return "CREATE TABLE " + stream.id().finalTableId();
  }

  @Override
  public String alterTable(final StreamConfig<StandardSQLTypeName> stream,
                           final TableDefinition existingTable) {
    if (existingTable instanceof StandardTableDefinition s) {
      // TODO check if clustering/partitioning config is different from what we want, do something to handle it
      // iirc this will depend on the stream (destination?) sync mode + cursor + pk name
      if (s.getClustering() != null) {

      }
    } else {
      // TODO idk
    }
    return null;
  }

  // We need the configuredairbytestream for the sync mode + cursor name
  @Override
  public String updateTable(String finalSuffix, final StreamConfig<StandardSQLTypeName> stream) {
    // TODO this method needs to handle all the sync modes
    // do the stuff that evan figured out how to do https://github.com/airbytehq/typing-and-deduping-sql/blob/main/one-table.postgres.sql#L153
    // TODO use a better string templating thing
    return String.format(
        """
            BEGIN;
                    
            INSERT INTO %s.%s
            SELECT
              TODO....
            FROM %s;
            
            DELETE from <final>
            WHERE <raw_id> IN (
             SELECT `_airbyte_raw_id` FROM (
               SELECT `_airbyte_raw_id`, row_number() OVER (
                 PARTITION BY `id` ORDER BY `updated_at` DESC, `_airbyte_extracted_at` DESC
               ) as row_number FROM evan.users
             )
             WHERE row_number != 1
           )
           OR
           -- Delete rows that have been CDC deleted
           `id` IN (
             SELECT
               SAFE_CAST(JSON_EXTRACT_SCALAR(`_airbyte_data`, '$.id') as INT64) as id -- based on the PK which we know from the connector catalog
             FROM evan.users_raw
             WHERE JSON_EXTRACT_SCALAR(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NOT NULL
           )
                    
            COMMIT;
            """,
        stream.id().finalNamespace(),
        // TODO this is wrong, we can't just do "`foo`.`bar`" + "_tmp"
        finalSuffix.length() > 0 ? stream.id().finalName() + "_" + finalSuffix : stream.id().finalName(),
        stream.id().rawTableId()
    );
  }

  @Override
  public String deleteOldRawRecords(final StreamConfig<StandardSQLTypeName> stream) {
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      // TODO maybe this should have an extracted_at / loaded_at condition for efficiency
      // We don't need to filter out `_airbyte_data ->> '_ab_cdc_deleted_at' IS NULL` because we can run this sql before executing CDC deletes
      return """
          DELETE FROM %s WHERE %s NOT IN (
            SELECT %s FROM %s
          )
          """.formatted(
          stream.id().rawTableId(),
          RAW_ID,
          RAW_ID,
          stream.id().finalTableId()
      );
    } else {
      return "";
    }
  }

  @Override
  public String overwriteFinalTable(final String finalSuffix, final StreamConfig<StandardSQLTypeName> stream) {
    if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE && finalSuffix.length() > 0) {
      return """
          DROP TABLE %s;
          ALTER TABLE %s RENAME TO %s;
          """.formatted(
          stream.id().finalTableId(),
          stream.id().rawTableId() + "_" + finalSuffix,
          stream.id().finalName()
      );
    } else {
      return "";
    }
  }
}
