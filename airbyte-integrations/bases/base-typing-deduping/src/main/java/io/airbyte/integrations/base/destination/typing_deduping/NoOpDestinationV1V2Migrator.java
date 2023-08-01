package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import java.util.Collection;
import java.util.Optional;

public class NoOpDestinationV1V2Migrator<DialectTableDefinition> implements DestinationV1V2Migrator {

  @Override
  public Optional<MigrationResult> migrateIfNecessary(SqlGenerator sqlGenerator, DestinationHandler destinationHandler,
      StreamConfig streamConfig) {
    return Optional.empty();
  }

  @Override
  public boolean shouldMigrate(StreamConfig streamConfig) {
    return false;
  }

  @Override
  public boolean doesAirbyteInternalNamespaceExist(StreamConfig streamConfig) {
    return true;
  }

  @Override
  public boolean schemaMatchesExpectation(Object existingTable, Collection columns) {
    return true;
  }

  @Override
  public Optional getTableIfExists(AirbyteStreamNameNamespacePair nameAndNamespacePair) {
    return Optional.empty();
  }

  @Override
  public AirbyteStreamNameNamespacePair convertToV1RawName(StreamConfig streamConfig) {
    return null;
  }
}
