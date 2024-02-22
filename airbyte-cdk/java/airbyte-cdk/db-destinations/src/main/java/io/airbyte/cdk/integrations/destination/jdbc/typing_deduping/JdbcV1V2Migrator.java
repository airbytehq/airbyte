/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.commons.exceptions.SQLRuntimeException;
import io.airbyte.integrations.base.destination.typing_deduping.BaseDestinationV1V2Migrator;
import io.airbyte.integrations.base.destination.typing_deduping.NamespacedTableName;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Collection;
import java.util.Optional;
import lombok.SneakyThrows;

/**
 * Largely based on
 * {@link io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV1V2Migrator}.
 */
public class JdbcV1V2Migrator extends BaseDestinationV1V2Migrator<TableDefinition> {

  private final NamingConventionTransformer namingConventionTransformer;
  private final JdbcDatabase database;
  private final String databaseName;

  public JdbcV1V2Migrator(final NamingConventionTransformer namingConventionTransformer, final JdbcDatabase database, final String databaseName) {
    this.namingConventionTransformer = namingConventionTransformer;
    this.database = database;
    this.databaseName = databaseName;
  }

  @SneakyThrows
  @Override
  protected boolean doesAirbyteInternalNamespaceExist(final StreamConfig streamConfig) {
    final String retrievedSchema = database.executeMetadataQuery(dbMetadata -> {
      try (ResultSet columns = dbMetadata.getSchemas(databaseName, streamConfig.id().rawNamespace())) {
        String schema = "";
        while (columns.next()) {
          // Catalog can be null, so don't do anything with it.
          // columns.getString("TABLE_CATALOG");
          schema = columns.getString("TABLE_SCHEM");
        }
        return schema;
      } catch (SQLException e) {
        throw new SQLRuntimeException(e);
      }
    });

    return !retrievedSchema.isEmpty();
  }

  @Override
  protected boolean schemaMatchesExpectation(final TableDefinition existingTable, final Collection<String> columns) {
    return existingTable.columns().keySet().containsAll(columns);
  }

  @SneakyThrows
  @Override
  protected Optional<TableDefinition> getTableIfExists(final String namespace, final String tableName) throws Exception {
    return JdbcDestinationHandler.findExistingTable(database, databaseName, namespace, tableName);
  }

  @Override
  protected NamespacedTableName convertToV1RawName(final StreamConfig streamConfig) {
    @SuppressWarnings("deprecation")
    final String tableName = this.namingConventionTransformer.getRawTableName(streamConfig.id().originalName());
    return new NamespacedTableName(
        this.namingConventionTransformer.getIdentifier(streamConfig.id().originalNamespace()),
        tableName);
  }

}
