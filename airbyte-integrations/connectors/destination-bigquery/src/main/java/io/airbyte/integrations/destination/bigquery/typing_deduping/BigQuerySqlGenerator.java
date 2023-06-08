package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableResult;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Object;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Primitive;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.UnsupportedOneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.StreamConfig;
import java.util.List;
import java.util.UUID;

public class BigQuerySqlGenerator implements SqlGenerator<TableDefinition, StandardSQLTypeName> {

  @Override
  public QuotedStreamId quoteStreamId(final String namespace, final String name) {
    // TODO
    return null;
  }

  @Override
  public QuotedColumnId quoteColumnId(final String name) {
    // TODO
    return null;
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
  public String updateTable(final StreamConfig<StandardSQLTypeName> stream) {
    // do the stuff that evan figured out how to do https://github.com/airbytehq/typing-and-deduping-sql/blob/main/one-table.postgres.sql#L153
    // TODO use a better string templating thing
    return String.format(
        """
        BEGIN;
        
        INSERT INTO %s.%s
        SELECT
          TODO....
        FROM airbyte._airbyte_raw_%s_%s
        
        COMMIT;
        """,
        stream.id().namespace(),
        stream.id().name(),
        stream.id().namespace(),
        stream.id().name()
    );
  }

  @Override
  public String executeCdcDeletions(final StreamConfig<StandardSQLTypeName> stream) {
    // TODO maybe this should have an extracted_at / loaded_at condition for efficiency
    return "DELETE FROM " + stream.id().finalTableId() + " WHERE _ab_cdc_deleted_at IS NOT NULL";
  }

  @Override
  public String deletePreviousSyncRecords(final StreamConfig<StandardSQLTypeName> stream, final UUID syncId) {
    // TODO maybe this should have an extracted_at / loaded_at condition for efficiency
    return "DELETE FROM " + stream.id().finalTableId() + " WHERE _airbyte_loaded_at != " + syncId;
  }

  public static void main(String[] args) throws InterruptedException {
    BigQuery bq = BigQueryOptions.newBuilder().setProjectId("dataline-integration-testing").build().getService();
    final TableResult query = bq.query(QueryJobConfiguration.newBuilder("select 1; select 2;").build());
    System.out.println(query);

    new UnsupportedOneOf(List.of(AirbyteType.Primitive.STRING));
  }
}
