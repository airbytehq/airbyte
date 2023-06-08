package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableResult;
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Object;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Primitive;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.UnsupportedOneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.StreamConfig;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public class BigQuerySqlGenerator implements SqlGenerator<TableDefinition, StandardSQLTypeName> {

  private static final BigQuerySQLNameTransformer nameTransformer = new BigQuerySQLNameTransformer();

  @Override
  public QuotedStreamId quoteStreamId(final String namespace, final String name) {
    // TODO is this correct?
    return new QuotedStreamId(
        nameTransformer.getNamespace(namespace),
        nameTransformer.convertStreamName(name),
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
      // TODO map data types
      return null;
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
    return null;
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
  public String updateTable(String rawSuffix, final StreamConfig<StandardSQLTypeName> stream) {
    // TODO this method needs to handle all the sync modes
    // do the stuff that evan figured out how to do https://github.com/airbytehq/typing-and-deduping-sql/blob/main/one-table.postgres.sql#L153
    // TODO use a better string templating thing
    return String.format(
        """
            BEGIN;
                    
            INSERT INTO %s.%s
            SELECT
              TODO....
            FROM airbyte.%s_%s
                    
            COMMIT;
            """,
        stream.id().namespace(),
        stream.id().name(),
        stream.id().namespace(),
        rawSuffix.length() > 0 ? stream.id().rawName() + "_" + rawSuffix : stream.id().rawName()
    );
  }

  @Override
  public String executeCdcDeletions(final StreamConfig<StandardSQLTypeName> stream) {
    // CDC is always incremental dedup
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      // TODO maybe this should have an extracted_at / loaded_at condition for efficiency
      return "DELETE FROM " + stream.id().finalTableId() + " WHERE _ab_cdc_deleted_at IS NOT NULL";
    } else {
      return "";
    }
  }

  @Override
  public String deleteOldRawRecords(final StreamConfig<StandardSQLTypeName> stream) {
    // We don't need to filter out `_airbyte_data ->> '_ab_cdc_deleted_at' IS NULL` because we can run this sql before executing CDC deletes
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      // TODO maybe this should have an extracted_at / loaded_at condition for efficiency
      return """
          DELETE FROM airbyte.%s WHERE _airbyte_raw_id NOT IN (
            SELECT _airbyte_raw_id FROM public.users
          )""".formatted(stream.id().rawName());
    } else {
      return "";
    }
  }

  @Override
  public String deletePreviousSyncRecords(final StreamConfig<StandardSQLTypeName> stream, final UUID syncId) {
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      // TODO maybe this should have an extracted_at / loaded_at condition for efficiency
      return "DELETE FROM " + stream.id().finalTableId() + " WHERE _airbyte_loaded_at != " + syncId;
    } else {
      return "";
    }
  }

}
