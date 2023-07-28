package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Collection;
import java.util.Optional;
import java.util.function.Supplier;
import lombok.Setter;

public class MockDestinationV1V2Migrator implements DestinationV1V2Migrator<String> {

  @Setter
  private MigrationResult migrationResultValue;

  @Setter
  private boolean shouldMigrateValue;

  @Setter
  private boolean doesV1RawTableMatchExpectedSchemaValue;

  @Setter
  private boolean doesAirbyteInternalNamespaceRawTableMatchExpectedV2SchemaValue;

  @Setter
  private boolean isMigrationRequiredForSyncModeValue;

  @Setter
  private boolean doesValidV2RawTableAlreadyExistValue;

  @Setter
  private boolean doesValidV1RawTableExistValue;

  @Setter
  private boolean doesAirbyteInternalNamespaceExistValue;

  @Setter
  private boolean schemaMatchesExpectationValue;

  @Setter
  private boolean getTableIfExistsValue;

  @Setter
  private boolean convertToV1RawNameValue;

  @Override
  public Optional<MigrationResult> migrateIfNecessary(SqlGenerator sqlGenerator, DestinationHandler destinationHandler,
      StreamConfig streamConfig) {
    return DestinationV1V2Migrator.super.migrateIfNecessary(sqlGenerator, destinationHandler, streamConfig);
  }

  @Override
  public boolean shouldMigrate(StreamConfig streamConfig) {
    return DestinationV1V2Migrator.super.shouldMigrate(streamConfig);
  }

  @Override
  public MigrationResult migrate(SqlGenerator sqlGenerator, DestinationHandler destinationHandler, StreamConfig streamConfig) {
    return DestinationV1V2Migrator.super.migrate(sqlGenerator, destinationHandler, streamConfig);
  }

  @Override
  public boolean doesV1RawTableMatchExpectedSchema(String existingV2AirbyteRawTable) {
    return DestinationV1V2Migrator.super.doesV1RawTableMatchExpectedSchema(existingV2AirbyteRawTable);
  }

  @Override
  public boolean doesAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(String existingV2AirbyteRawTable) {
    return DestinationV1V2Migrator.super.doesAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(existingV2AirbyteRawTable);
  }

  @Override
  public boolean isMigrationRequiredForSyncMode(SyncMode syncMode, DestinationSyncMode destinationSyncMode) {
    return DestinationV1V2Migrator.super.isMigrationRequiredForSyncMode(syncMode, destinationSyncMode);
  }

  @Override
  public boolean doesValidV2RawTableAlreadyExist(StreamConfig streamConfig) {
    return overrideOrSuper(() -> DestinationV1V2Migrator.super.doesValidV2RawTableAlreadyExist(streamConfig), doesValidV2RawTableAlreadyExistValue);
  }

  @Override
  public boolean doesValidV1RawTableExist(AirbyteStreamNameNamespacePair rawTableNamePair) {
    return overrideOrSuper(() -> DestinationV1V2Migrator.super.doesValidV1RawTableExist(rawTableNamePair), doesValidV1RawTableExistValue);
  }

  @Override
  public boolean doesAirbyteInternalNamespaceExist(StreamConfig streamConfig) {
    return false;
  }

  @Override
  public boolean schemaMatchesExpectation(String existingTable, Collection columns) {
    return false;
  }

  @Override
  public Optional<String> getTableIfExists(AirbyteStreamNameNamespacePair nameAndNamespacePair) {
    return Optional.empty();
  }

  @Override
  public AirbyteStreamNameNamespacePair convertToV1RawName(StreamConfig streamConfig) {
    return null;
  }

  private <T> T overrideOrSuper(Supplier<T> superMethod, T overrideValue) {
    return overrideValue != null ? overrideValue : superMethod.get();
  }
}
