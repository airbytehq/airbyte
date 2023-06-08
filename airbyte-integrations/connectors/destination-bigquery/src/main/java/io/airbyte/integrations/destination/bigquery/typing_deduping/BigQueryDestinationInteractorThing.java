package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import io.airbyte.integrations.destination.bigquery.typing_deduping.SqlGenerator.QuotedStreamId;
import java.util.Optional;

// TODO this stuff almost definitely exists somewhere else in our codebase.
public class BigQueryDestinationInteractorThing implements DestinationInteractorThing<TableDefinition> {

  private final BigQuery bq;

  public BigQueryDestinationInteractorThing(final BigQuery bq) {
    this.bq = bq;
  }

  @Override
  public Optional<TableDefinition> findExistingTable(QuotedStreamId id) {
    final Table table = bq.getTable(id.namespace(), id.name());
    return Optional.ofNullable(table).map(Table::getDefinition);
  }

  @Override
  public void execute(final String sql) throws InterruptedException {
    bq.query(QueryJobConfiguration.newBuilder(sql).build());
  }
}
