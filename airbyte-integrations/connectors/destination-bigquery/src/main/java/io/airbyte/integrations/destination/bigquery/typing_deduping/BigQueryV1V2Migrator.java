package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationV1V2Migrator;
import io.airbyte.integrations.base.destination.typing_deduping.MigrationResult;
import io.airbyte.integrations.base.destination.typing_deduping.NameAndNamespacePair;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.protocol.models.v1.DestinationSyncMode;
import io.airbyte.protocol.models.v1.SyncMode;
import java.util.Collection;
import java.util.Collections;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

public class BigQueryV1V2Migrator implements DestinationV1V2Migrator<TableDefinition> {

  private final BigQuery bq;
  private final BigQuerySqlGenerator bQsqlGenerator;
  private final BigQueryDestinationHandler bQdestinationHandler;

  public BigQueryV1V2Migrator(final BigQuery bq, BigQuerySqlGenerator bqSqlGenerator, BigQueryDestinationHandler bQdestinationHandler) {
    this.bq = bq;
    this.bQsqlGenerator = bqSqlGenerator;
    this.bQdestinationHandler = bQdestinationHandler;
  }

  public Optional<MigrationResult> migrateIfNecessary(SyncMode syncMode, DestinationSyncMode destinationSyncMode, StreamConfig streamConfig,
      NameAndNamespacePair v1RawTableNameAndNamespace) {
    return migrateIfNecessary(syncMode, destinationSyncMode, this.bQsqlGenerator, this.bQdestinationHandler, streamConfig,
        v1RawTableNameAndNamespace);
  }

  @Override
  public boolean doesAirbyteNamespaceExist(StreamConfig streamConfig) {
    return bq.getDataset(streamConfig.id().rawNamespace()).exists();
  }

  @Override
  public Optional<TableDefinition> getTableIfExists(NameAndNamespacePair nameAndNamespacePair) {
    Table table = bq.getTable(TableId.of(nameAndNamespacePair.namespace(), nameAndNamespacePair.tableName()));
    return table.exists() ? Optional.of(table.getDefinition()) : Optional.empty();
  }

  @Override
  public boolean schemaMatchesExpectation(TableDefinition existingTable, Collection<String> expectedColumnNames) {
    Set<String> existingSchemaColumns = Optional.ofNullable(existingTable.getSchema())
        .map(schema -> schema.getFields().stream()
            .map(Field::getName)
            .collect(Collectors.toSet()))
        .orElse(Collections.emptySet());

    // TODO maybe add type checking as well?

    return !existingSchemaColumns.isEmpty() &&
        CollectionUtils.containsAllIgnoreCase(expectedColumnNames, existingSchemaColumns);
  }
}
