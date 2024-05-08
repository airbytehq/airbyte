/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler.*;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.integrations.base.destination.typing_deduping.BaseDestinationV1V2Migrator;
import io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils;
import io.airbyte.integrations.base.destination.typing_deduping.NamespacedTableName;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.Optional;
import lombok.SneakyThrows;

public class SnowflakeV1V2Migrator extends BaseDestinationV1V2Migrator<TableDefinition> {

  private final NamingConventionTransformer namingConventionTransformer;

  private final JdbcDatabase database;

  private final String databaseName;

  public SnowflakeV1V2Migrator(final NamingConventionTransformer namingConventionTransformer,
                               final JdbcDatabase database,
                               final String databaseName) {
    this.namingConventionTransformer = namingConventionTransformer;
    this.database = database;
    this.databaseName = databaseName;
  }

  @SneakyThrows
  @Override
  public boolean doesAirbyteInternalNamespaceExist(final StreamConfig streamConfig) throws Exception {
    return !database
        .queryJsons(
            """
            SELECT SCHEMA_NAME
            FROM information_schema.schemata
            WHERE schema_name = ?
            AND catalog_name = ?;
            """,
            streamConfig.getId().getRawNamespace(),
            databaseName)
        .isEmpty();
  }

  @Override
  public boolean schemaMatchesExpectation(final TableDefinition existingTable, final Collection<String> columns) {
    return CollectionUtils.containsAllIgnoreCase(existingTable.columns().keySet(), columns);
  }

  @SneakyThrows
  @Override
  public Optional<TableDefinition> getTableIfExists(final String namespace, final String tableName) throws Exception {
    // TODO this looks similar to SnowflakeDestinationHandler#findExistingTables, with a twist;
    // databaseName not upper-cased and rawNamespace and rawTableName as-is (no uppercase).
    // The obvious database.getMetaData().getColumns() solution doesn't work, because JDBC translates
    // VARIANT as VARCHAR
    final LinkedHashMap<String, ColumnDefinition> columns =
        database.queryJsons(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_catalog = ?
              AND table_schema = ?
              AND table_name = ?
            ORDER BY ordinal_position;
            """,
            databaseName,
            namespace,
            tableName)
            .stream()
            .collect(LinkedHashMap::new,
                (map, row) -> map.put(row.get("COLUMN_NAME").asText(),
                    new ColumnDefinition(row.get("COLUMN_NAME").asText(), row.get("DATA_TYPE").asText(), 0,
                        fromIsNullableIsoString(row.get("IS_NULLABLE").asText()))),
                LinkedHashMap::putAll);
    if (columns.isEmpty()) {
      return Optional.empty();
    } else {
      return Optional.of(new TableDefinition(columns));
    }
  }

  @Override
  public NamespacedTableName convertToV1RawName(final StreamConfig streamConfig) {
    // The implicit upper-casing happens for this in the SqlGenerator
    @SuppressWarnings("deprecation")
    String tableName = this.namingConventionTransformer.getRawTableName(streamConfig.getId().getOriginalName());
    return new NamespacedTableName(
        this.namingConventionTransformer.getIdentifier(streamConfig.getId().getOriginalNamespace()),
        tableName);
  }

  @Override
  protected boolean doesValidV1RawTableExist(final String namespace, final String tableName) throws Exception {
    // Previously we were not quoting table names and they were being implicitly upper-cased.
    // In v2 we preserve cases
    return super.doesValidV1RawTableExist(namespace.toUpperCase(), tableName.toUpperCase());
  }

}
