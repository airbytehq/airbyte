package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableResult;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.OneOf;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.LinkedHashMap;
import java.util.List;

public class BigQuerySqlGenerator implements SqlGenerator<TableDefinition> {

  @Override
  public SanitizedTableIdentifier sanitizeNames(final String namespace, final String name) {
    return null;
  }

  @Override
  public String createTable(final SanitizedTableIdentifier id, final ConfiguredAirbyteStream stream, final LinkedHashMap<String, AirbyteType> types) {
    return "CREATE TABLE ";
  }

  @Override
  public String alterTable(final SanitizedTableIdentifier id,
                           final ConfiguredAirbyteStream stream,
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
  public String updateTable(final SanitizedTableIdentifier id, final ConfiguredAirbyteStream stream, final LinkedHashMap<String, AirbyteType> types) {
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
        id.namespace(),
        id.name(),
        id.namespace(),
        id.name()
    );
  }

  public static void main(String[] args) throws InterruptedException {
    BigQuery bq = BigQueryOptions.newBuilder().setProjectId("dataline-integration-testing").build().getService();
    final TableResult query = bq.query(QueryJobConfiguration.newBuilder("select 1; select 2;").build());
    System.out.println(query);

    new OneOf(List.of(AirbyteType.Primitive.STRING));
  }
}
