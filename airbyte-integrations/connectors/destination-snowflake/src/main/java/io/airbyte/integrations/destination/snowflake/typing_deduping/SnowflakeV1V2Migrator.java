/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.BaseDestinationV1V2Migrator;
import io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils;
import io.airbyte.integrations.base.destination.typing_deduping.NamespacedTableName;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.Optional;
import lombok.SneakyThrows;

public class SnowflakeV1V2Migrator extends BaseDestinationV1V2Migrator<SnowflakeTableDefinition> {

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
  protected boolean doesAirbyteInternalNamespaceExist(final StreamConfig streamConfig) {
    return !database
        .queryJsons(
            """
            SELECT SCHEMA_NAME
            FROM information_schema.schemata
            WHERE schema_name = ?
            AND catalog_name = ?;
            """,
            streamConfig.id().rawNamespace(),
            databaseName)
        .isEmpty();
  }

  @Override
  protected boolean schemaMatchesExpectation(final SnowflakeTableDefinition existingTable, final Collection<String> columns) {
    return CollectionUtils.containsAllIgnoreCase(existingTable.columns().keySet(), columns);
  }

  @SneakyThrows
  @Override
  protected Optional<SnowflakeTableDefinition> getTableIfExists(final String namespace, final String tableName) {
    // TODO this is mostly copied from SnowflakeDestinationHandler#findExistingTable, we should probably
    // reuse this logic
    // The obvious database.getMetaData().getColumns() solution doesn't work, because JDBC translates
    // VARIANT as VARCHAR
    LinkedHashMap<String, String> columns =
        database.queryJsons(
            """
            SELECT column_name, data_type
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
                (map, row) -> map.put(row.get("COLUMN_NAME").asText(), row.get("DATA_TYPE").asText()),
                LinkedHashMap::putAll);
    if (columns.isEmpty()) {
      return Optional.empty();
    } else {
      return Optional.of(new SnowflakeTableDefinition(columns));
    }
  }

  @Override
  protected NamespacedTableName convertToV1RawName(final StreamConfig streamConfig) {
    // The implicit upper-casing happens for this in the SqlGenerator
    return new NamespacedTableName(
        this.namingConventionTransformer.getIdentifier(streamConfig.id().originalNamespace()),
        this.namingConventionTransformer.getRawTableName(streamConfig.id().originalName()));
  }

  @Override
  protected boolean doesValidV1RawTableExist(final String namespace, final String tableName) {
    // Previously we were not quoting table names and they were being implicitly upper-cased.
    // In v2 we preserve cases
    return super.doesValidV1RawTableExist(namespace.toUpperCase(), tableName.toUpperCase());
  }

}
