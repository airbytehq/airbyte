package io.airbyte.integrations.destination.snowflake.typing_deduping;

import io.airbyte.integrations.base.destination.typing_deduping.BaseDestinationV1V2Migrator;
import io.airbyte.integrations.base.destination.typing_deduping.NamespacedTableName;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import java.util.Collection;
import java.util.Optional;

public class SnowflakeV1V2Migrator extends BaseDestinationV1V2Migrator<SnowflakeTableDefinition> {

  @Override
  protected boolean doesAirbyteInternalNamespaceExist(final StreamConfig streamConfig) {
    return false;
  }

  @Override
  protected boolean schemaMatchesExpectation(final SnowflakeTableDefinition existingTable, final Collection<String> columns) {
    return false;
  }

  @Override
  protected Optional<SnowflakeTableDefinition> getTableIfExists(final String namespace, final String tableName) {
    return Optional.empty();
  }

  @Override
  protected NamespacedTableName convertToV1RawName(final StreamConfig streamConfig) {
    return null;
  }
}
