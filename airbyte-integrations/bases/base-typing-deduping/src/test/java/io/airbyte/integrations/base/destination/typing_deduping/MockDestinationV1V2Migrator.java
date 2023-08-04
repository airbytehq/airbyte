package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.Collection;
import java.util.Optional;
import java.util.function.Supplier;
import lombok.NoArgsConstructor;
import lombok.Setter;

@NoArgsConstructor
public class MockDestinationV1V2Migrator extends BaseDestinationV1V2Migrator<String> {

  @Setter
  private Boolean shouldMigrateValue;

//  @Setter
//  private Boolean doesV1RawTableMatchExpectedSchemaValue;
//
//  @Setter
//  private Boolean doesAirbyteInternalNamespaceRawTableMatchExpectedV2SchemaValue;
//
//  @Setter
//  private Boolean isMigrationRequiredForSyncModeValue;
//
//  @Setter
//  private Boolean doesValidV2RawTableAlreadyExistValue;
//
//  @Setter
//  private Boolean doesValidV1RawTableExistValue;

  @Setter
  private Boolean doesAirbyteInternalNamespaceExistValue;

  @Setter
  private Boolean schemaMatchesExpectationValue;

  @Setter
  private String getTableIfExistsValue;

  @Setter
  private NamespacedTableName convertToV1RawNameValue;

  public static MockDestinationV1V2Migrator shouldMigrateBuilder(final boolean doesValidV2RawTableAlreadyExist,
      final boolean doesValidV1RawTableExist) {
    final var migrator = new MockDestinationV1V2Migrator();
//    migrator.setIsMigrationRequiredForSyncModeValue(isMigrationRequiredForSyncMode);
//    migrator.setDoesValidV2RawTableAlreadyExistValue(doesValidV2RawTableAlreadyExist);
//    migrator.setDoesValidV1RawTableExistValue(doesValidV1RawTableExist);
    return migrator;
  }

  @Override
  public boolean shouldMigrate(StreamConfig streamConfig) {
    return overrideOrSuper(() -> super.shouldMigrate(streamConfig), shouldMigrateValue);
  }

//  @Override
//  public void migrate(SqlGenerator sqlGenerator, DestinationHandler destinationHandler, StreamConfig streamConfig) {
//    return overrideOrSuper(() -> super.migrate(sqlGenerator, destinationHandler, streamConfig), migrationResultValue);
//  }

//  @Override
//  public boolean doesV1RawTableMatchExpectedSchema(String existingV2AirbyteRawTable) {
//    return overrideOrSuper(() -> super.doesV1RawTableMatchExpectedSchema(existingV2AirbyteRawTable),
//        doesV1RawTableMatchExpectedSchemaValue);
//  }

//  @Override
//  public boolean doesAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(String existingV2AirbyteRawTable) {
//    return overrideOrSuper(
//        () -> super.doesAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(existingV2AirbyteRawTable),
//        doesAirbyteInternalNamespaceRawTableMatchExpectedV2SchemaValue);
//  }

//  @Override
//  public boolean isMigrationRequiredForSyncMode(SyncMode syncMode, DestinationSyncMode destinationSyncMode) {
//    return overrideOrSuper(() -> super.isMigrationRequiredForSyncMode(syncMode, destinationSyncMode),
//        isMigrationRequiredForSyncModeValue);
//  }

//  @Override
//  public boolean doesValidV2RawTableAlreadyExist(StreamConfig streamConfig) {
//    return overrideOrSuper(() -> super.doesValidV2RawTableAlreadyExist(streamConfig),
//        doesValidV2RawTableAlreadyExistValue);
//  }

//  @Override
//  public boolean doesValidV1RawTableExist(AirbyteStreamNameNamespacePair rawTableNamePair) {
//    return overrideOrSuper(() -> BaseDestinationV1V2Migrator.super.doesValidV1RawTableExist(rawTableNamePair), doesValidV1RawTableExistValue);
//  }

  @Override
  protected boolean doesAirbyteInternalNamespaceExist(StreamConfig streamConfig) {
    return doesAirbyteInternalNamespaceExistValue;
  }

  @Override
  protected boolean schemaMatchesExpectation(String existingTable, Collection columns) {
    return schemaMatchesExpectationValue;
  }

  @Override
  protected Optional<String> getTableIfExists(String namespace, String tableName) {
    return Optional.ofNullable(getTableIfExistsValue);
  }

  @Override
  protected NamespacedTableName convertToV1RawName(StreamConfig streamConfig) {
    return convertToV1RawNameValue;
  }

  private <T> T overrideOrSuper(Supplier<T> superMethod, T overrideValue) {
    return overrideValue != null ? overrideValue : superMethod.get();
  }
}
