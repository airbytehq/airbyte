package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.protocol.models.v1.DestinationSyncMode;
import io.airbyte.protocol.models.v1.SyncMode;

import java.util.Optional;

public interface DestinationV1V2Migrator<DialectTableDefinition> {
    MigrationResult migrate(final SqlGenerator<DialectTableDefinition> sqlGenerator,
                            final DestinationHandler<DialectTableDefinition> destinationHandler,
                            final StreamConfig streamConfig);

    boolean doesAirbyteNamespaceExist(StreamConfig streamConfig);

    Optional<DialectTableDefinition> getRawTableFromAirbyteSchemaIfExists(final StreamConfig streamConfig);

    boolean doesAirbyteNamespaceRawTableMatchExpectedV2Schema(DialectTableDefinition existingV2AirbyteRawTable)
            throws Exception;

    Optional<DialectTableDefinition> getV1RawTableIfExists(NameAndNamespacePair v1RawTableNamespacePair);

    boolean doesV1RawTableMatchExpectedSchema(DialectTableDefinition existingV2AirbyteRawTable);

    default boolean isMigrationRequiredForSyncMode(final SyncMode syncMode, final DestinationSyncMode destinationSyncMode) {
        return !(SyncMode.FULL_REFRESH.equals(syncMode) && DestinationSyncMode.OVERWRITE.equals(destinationSyncMode));
    }

    default boolean doesValidV2RawTableAlreadyExist(final StreamConfig streamConfig) throws Exception {
        if (doesAirbyteNamespaceExist(streamConfig)) {
            final var existingV2Table = getRawTableFromAirbyteSchemaIfExists(streamConfig);
            return existingV2Table.isPresent() && doesAirbyteNamespaceRawTableMatchExpectedV2Schema(existingV2Table.get());
        }
        return false;
    }

    default boolean doesValidV1RawTableExist(NameAndNamespacePair rawTableNamePair) {
        final var existingV1RawTable = getV1RawTableIfExists(rawTableNamePair);
        return existingV1RawTable.isPresent() && doesV1RawTableMatchExpectedSchema(existingV1RawTable.get());
    }

    default boolean shouldMigrate(SyncMode syncMode,
                                  DestinationSyncMode destinationSyncMode,
                                  final StreamConfig streamConfig,
                                  NameAndNamespacePair v1RawNameNamespacePair) throws Exception {
        return isMigrationRequiredForSyncMode(syncMode, destinationSyncMode)
                && !doesValidV2RawTableAlreadyExist(streamConfig)
                && doesValidV1RawTableExist(v1RawNameNamespacePair);
    }

    default Optional<MigrationResult> migrateIfNecessary(SyncMode syncMode,
                                                         DestinationSyncMode destinationSyncMode,
                                                         final SqlGenerator<DialectTableDefinition> sqlGenerator,
                                                         final DestinationHandler<DialectTableDefinition> destinationHandler,
                                                         final StreamConfig streamConfig, NameAndNamespacePair v1RawNameNamespacePair) throws Exception {
        if (shouldMigrate(syncMode, destinationSyncMode, streamConfig, v1RawNameNamespacePair)) {
            return Optional.of(migrate(sqlGenerator, destinationHandler, streamConfig));
        } else {
            return Optional.empty();
        }
    }
}
