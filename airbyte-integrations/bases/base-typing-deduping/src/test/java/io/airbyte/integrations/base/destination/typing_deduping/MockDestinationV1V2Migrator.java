package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Collection;
import java.util.Optional;
import java.util.function.Supplier;
import lombok.NoArgsConstructor;
import lombok.Setter;

@NoArgsConstructor
public class MockDestinationV1V2Migrator implements DestinationV1V2Migrator<String> {

  @Setter
  private MigrationResult migrationResultValue;

  @Setter
  private Boolean shouldMigrateValue;

  @Setter
  private Boolean doesV1RawTableMatchExpectedSchemaValue;

  @Setter
  private Boolean doesAirbyteInternalNamespaceRawTableMatchExpectedV2SchemaValue;

  @Setter
  private Boolean isMigrationRequiredForSyncModeValue;

  @Setter
  private Boolean doesValidV2RawTableAlreadyExistValue;

  @Setter
  private Boolean doesValidV1RawTableExistValue;

  @Setter
  private Boolean doesAirbyteInternalNamespaceExistValue;

  @Setter
  private Boolean schemaMatchesExpectationValue;

  @Setter
  private String getTableIfExistsValue;

  @Setter
  private AirbyteStreamNameNamespacePair convertToV1RawNameValue;

  public static MockDestinationV1V2Migrator shouldMigrateBuilder(final boolean isMigrationRequiredForSyncMode,
      final boolean doesValidV2RawTableAlreadyExist,
      final boolean doesValidV1RawTableExist) {
    final var migrator = new MockDestinationV1V2Migrator();
    migrator.setIsMigrationRequiredForSyncModeValue(isMigrationRequiredForSyncMode);
    migrator.setDoesValidV2RawTableAlreadyExistValue(doesValidV2RawTableAlreadyExist);
    migrator.setDoesValidV1RawTableExistValue(doesValidV1RawTableExist);
    return migrator;
  }

  @Override
  public boolean shouldMigrate(StreamConfig streamConfig) {
    return overrideOrSuper(() -> DestinationV1V2Migrator.super.shouldMigrate(streamConfig), shouldMigrateValue);
  }

  @Override
  public MigrationResult migrate(SqlGenerator sqlGenerator, DestinationHandler destinationHandler, StreamConfig streamConfig) {
    return overrideOrSuper(() -> DestinationV1V2Migrator.super.migrate(sqlGenerator, destinationHandler, streamConfig), migrationResultValue);
  }

  @Override
  public boolean doesV1RawTableMatchExpectedSchema(String existingV2AirbyteRawTable) {
    return overrideOrSuper(() -> DestinationV1V2Migrator.super.doesV1RawTableMatchExpectedSchema(existingV2AirbyteRawTable),
        doesV1RawTableMatchExpectedSchemaValue);
  }

  @Override
  public boolean doesAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(String existingV2AirbyteRawTable) {
    return overrideOrSuper(() -> DestinationV1V2Migrator.super.doesAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(existingV2AirbyteRawTable),
        doesAirbyteInternalNamespaceRawTableMatchExpectedV2SchemaValue);
  }

  @Override
  public boolean isMigrationRequiredForSyncMode(SyncMode syncMode, DestinationSyncMode destinationSyncMode) {
    return overrideOrSuper(() -> DestinationV1V2Migrator.super.isMigrationRequiredForSyncMode(syncMode, destinationSyncMode),
        isMigrationRequiredForSyncModeValue);
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
    return doesAirbyteInternalNamespaceExistValue;
  }

  @Override
  public boolean schemaMatchesExpectation(String existingTable, Collection columns) {
    return schemaMatchesExpectationValue;
  }

  @Override
  public Optional<String> getTableIfExists(AirbyteStreamNameNamespacePair nameAndNamespacePair) {
    return Optional.ofNullable(getTableIfExistsValue);
  }

  @Override
  public AirbyteStreamNameNamespacePair convertToV1RawName(StreamConfig streamConfig) {
    return convertToV1RawNameValue;
  }

  private <T> T overrideOrSuper(Supplier<T> superMethod, T overrideValue) {
    return overrideValue != null ? overrideValue : superMethod.get();
  }
}
