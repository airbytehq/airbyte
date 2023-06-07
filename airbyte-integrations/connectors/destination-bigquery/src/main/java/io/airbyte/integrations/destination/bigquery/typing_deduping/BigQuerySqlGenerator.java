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
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Primitive;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.UnsupportedOneOf;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.LinkedHashMap;
import java.util.List;

public class BigQuerySqlGenerator implements SqlGenerator<TableDefinition, StandardSQLTypeName> {

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

  @Override
  public String createTable(final ConfiguredAirbyteStream stream, final LinkedHashMap<String, AirbyteType> types) {
    return "CREATE TABLE ";
  }

  @Override
  public String alterTable(final ConfiguredAirbyteStream stream,
                           final LinkedHashMap<String, AirbyteType> types,
                           final TableDefinition existingTable) {
    if (existingTable instanceof StandardTableDefinition s) {
      // TODO check if clustering/partitioning config is different from what we want, do something to handle it
      if (s.getClustering() != null) {

      }
    } else {
      // TODO idk
    }
    return null;
  }

  // We need the configuredairbytestream for the sync mode + cursor name
  @Override
  public String updateTable(final ConfiguredAirbyteStream stream, final LinkedHashMap<String, AirbyteType> types) {
    // do the stuff that evan figured out how to do https://github.com/airbytehq/typing-and-deduping-sql/blob/main/one-table.postgres.sql#L153
    // TODO use a better string templating thing
    return String.format(
        """
        BEGIN;
        
        INSERT INTO %s.%s
        SELECT
          TODO....
        FROM %s._airbyte_raw_%s
        
        COMMIT;
        """,
        stream.getStream().getNamespace(),
        stream.getStream().getName(),
        stream.getStream().getNamespace(),
        stream.getStream().getName()
    );
  }

  public static void main(String[] args) throws InterruptedException {
    BigQuery bq = BigQueryOptions.newBuilder().setProjectId("dataline-integration-testing").build().getService();
    final TableResult query = bq.query(QueryJobConfiguration.newBuilder("select 1; select 2;").build());
    System.out.println(query);

    new UnsupportedOneOf(List.of(AirbyteType.Primitive.STRING));
  }
}
