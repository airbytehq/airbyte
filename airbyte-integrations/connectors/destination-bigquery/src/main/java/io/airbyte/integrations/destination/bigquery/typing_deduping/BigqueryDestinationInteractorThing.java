package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import java.util.Optional;

public class BigqueryDestinationInteractorThing implements DestinationInteractorThing<TableDefinition> {

  private final BigQuery bq;

  public BigqueryDestinationInteractorThing(final BigQuery bq) {
    this.bq = bq;
  }

  @Override
  public Optional<TableDefinition> findExistingTable(String namespace, String name) {
    // TODO sanitize these names
    final Table table = bq.getTable(namespace, name);
    return Optional.ofNullable(table).map(Table::getDefinition);
  }

  @Override
  public void execute(final String sql) throws InterruptedException {
    bq.query(QueryJobConfiguration.newBuilder(sql).build());
  }
}
