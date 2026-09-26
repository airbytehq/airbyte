/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.bigquery;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.gax.paging.Page;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetId;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.LegacySQLTypeName;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableId;
import io.airbyte.cdk.db.bigquery.BigQueryDatabase;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.CommonField;
import java.io.IOException;
import java.util.List;
import org.junit.jupiter.api.Test;

class BigQuerySourceTest {

  @Test
  public void testEmptyDatasetIdInConfig() throws IOException {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config_empty_datasetid.json"));
    final JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertTrue(dbConfig.get(BigQuerySource.CONFIG_DATASET_ID).isEmpty());
  }

  @Test
  public void testMissingDatasetIdInConfig() throws IOException {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config_missing_datasetid.json"));
    final JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertFalse(dbConfig.hasNonNull(BigQuerySource.CONFIG_DATASET_ID));
  }

  @Test
  public void testNullDatasetIdInConfig() throws IOException {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config_null_datasetid.json"));
    final JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertFalse(dbConfig.hasNonNull(BigQuerySource.CONFIG_DATASET_ID));
  }

  @Test
  public void testConfig() throws IOException {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config.json"));
    final JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertEquals("dataset", dbConfig.get(BigQuerySource.CONFIG_DATASET_ID).asText());
    assertEquals("project", dbConfig.get(BigQuerySource.CONFIG_PROJECT_ID).asText());
    assertEquals("credentials", dbConfig.get(BigQuerySource.CONFIG_CREDS).asText());
  }

  @Test
  public void testProjectDatasetNotFoundIsSkipped() throws Exception {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config_missing_datasetid.json"));
    final BigQuerySource source = newSourceWithConfig(configJson);
    final BigQueryDatabase database = mock(BigQueryDatabase.class);
    final BigQuery bigQuery = mock(BigQuery.class);
    final Dataset missingDataset = mock(Dataset.class);
    final Dataset validDataset = mock(Dataset.class);
    final Table table = mock(Table.class);
    final Table fullTable = mock(Table.class);
    final TableId tableId = TableId.of("project", "valid_dataset", "valid_table");
    final DatasetId missingDatasetId = DatasetId.of("project", "missing_dataset");
    final DatasetId validDatasetId = DatasetId.of("project", "valid_dataset");
    when(database.getSourceConfig()).thenReturn(configJson);
    when(database.getBigQuery()).thenReturn(bigQuery);
    when(bigQuery.listDatasets("xxxx")).thenReturn(page(List.of(missingDataset, validDataset)));
    when(missingDataset.getDatasetId()).thenReturn(missingDatasetId);
    when(validDataset.getDatasetId()).thenReturn(validDatasetId);
    when(bigQuery.listTables(missingDatasetId)).thenThrow(new BigQueryException(404, "Not found: Dataset project:missing_dataset"));
    when(bigQuery.listTables(validDatasetId)).thenReturn(page(List.of(table)));
    when(table.getTableId()).thenReturn(tableId);
    when(bigQuery.getTable(tableId)).thenReturn(fullTable);
    when(fullTable.getTableId()).thenReturn(tableId);
    when(fullTable.getDefinition()).thenReturn(StandardTableDefinition.of(Schema.of(Field.of("id", LegacySQLTypeName.STRING))));

    final List<TableInfo<CommonField<StandardSQLTypeName>>> tables = source.discoverInternal(database, null);
    assertEquals(1, tables.size());
    assertEquals("valid_dataset", tables.get(0).getNameSpace());
    assertEquals("valid_table", tables.get(0).getName());
  }

  @Test
  public void testConfiguredDatasetNotFoundIsConfigError() throws Exception {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config.json"));
    final BigQuerySource source = newSourceWithConfig(configJson);
    final BigQueryDatabase database = mock(BigQueryDatabase.class);
    when(database.getSourceConfig()).thenReturn(configJson);
    when(database.getDatasetTables("dataset")).thenThrow(new BigQueryException(404, "Not found: Dataset project:dataset"));

    final ConfigErrorException exception = assertThrows(ConfigErrorException.class, () -> source.discoverInternal(database, null));
    assertEquals("BigQuery dataset is not accessible. Verify the dataset exists and credentials have access.", exception.getDisplayMessage());
  }

  private BigQuerySource newSourceWithConfig(final JsonNode configJson) throws ReflectiveOperationException {
    final BigQuerySource source = new BigQuerySource();
    final java.lang.reflect.Field dbConfigField = BigQuerySource.class.getDeclaredField("dbConfig");
    dbConfigField.setAccessible(true);
    dbConfigField.set(source, configJson);
    return source;
  }

  private static <T> Page<T> page(final Iterable<T> values) {
    return new Page<>() {

      @Override
      public boolean hasNextPage() {
        return false;
      }

      @Override
      public String getNextPageToken() {
        return null;
      }

      @Override
      public Page<T> getNextPage() {
        return null;
      }

      @Override
      public Iterable<T> iterateAll() {
        return values;
      }

      @Override
      public Iterable<T> getValues() {
        return values;
      }

    };
  }

}
