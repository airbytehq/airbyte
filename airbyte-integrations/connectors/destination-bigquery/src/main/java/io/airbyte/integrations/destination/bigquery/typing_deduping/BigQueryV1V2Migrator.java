/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import io.airbyte.integrations.base.destination.typing_deduping.BaseDestinationV1V2Migrator;
import io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils;
import io.airbyte.integrations.base.destination.typing_deduping.NamespacedTableName;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer;
import java.util.Collection;
import java.util.Collections;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

public class BigQueryV1V2Migrator extends BaseDestinationV1V2Migrator<TableDefinition> {

  private final BigQuery bq;

  private final BigQuerySQLNameTransformer nameTransformer;

  public BigQueryV1V2Migrator(final BigQuery bq, BigQuerySQLNameTransformer nameTransformer) {
    this.bq = bq;
    this.nameTransformer = nameTransformer;
  }

  @Override
  public boolean doesAirbyteInternalNamespaceExist(StreamConfig streamConfig) {
    final var dataset = bq.getDataset(streamConfig.getId().getRawNamespace());
    return dataset != null && dataset.exists();
  }

  @Override
  public Optional<TableDefinition> getTableIfExists(String namespace, String tableName) {
    Table table = bq.getTable(TableId.of(namespace, tableName));
    return table != null && table.exists() ? Optional.of(table.getDefinition()) : Optional.empty();
  }

  @Override
  public boolean schemaMatchesExpectation(TableDefinition existingTable, Collection<String> expectedColumnNames) {
    Set<String> existingSchemaColumns = Optional.ofNullable(existingTable.getSchema())
        .map(schema -> schema.getFields().stream()
            .map(Field::getName)
            .collect(Collectors.toSet()))
        .orElse(Collections.emptySet());

    return !existingSchemaColumns.isEmpty() &&
        CollectionUtils.containsAllIgnoreCase(expectedColumnNames, existingSchemaColumns);
  }

  @Override
  @SuppressWarnings("deprecation")
  public NamespacedTableName convertToV1RawName(StreamConfig streamConfig) {
    return new NamespacedTableName(
        this.nameTransformer.getNamespace(streamConfig.getId().getOriginalNamespace()),
        this.nameTransformer.getRawTableName(streamConfig.getId().getOriginalName()));
  }

}
