package io.airbyte.integrations.base.destination.typing_deduping;

import static io.airbyte.integrations.base.destination.typing_deduping.Constants.RAW_TABLE_EXPECTED_V1_COLUMNS;
import static io.airbyte.integrations.base.destination.typing_deduping.Constants.RAW_TABLE_EXPECTED_V2_COLUMNS;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Collection;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public interface DestinationV1V2Migrator<DialectTableDefinition> {

    Logger LOGGER = LoggerFactory.getLogger(DestinationV1V2Migrator.class);

    default Optional<MigrationResult> migrateIfNecessary(
        final SqlGenerator<DialectTableDefinition> sqlGenerator,
        final DestinationHandler<DialectTableDefinition> destinationHandler,
        final StreamConfig streamConfig
    ) {
        if (shouldMigrate(streamConfig)) {
            LOGGER.info("Starting v2 Migration for stream {}", streamConfig.id().finalName());
            return Optional.of(migrate(sqlGenerator, destinationHandler, streamConfig));
        } else {
            return Optional.empty();
        }
    }

    default boolean shouldMigrate(final StreamConfig streamConfig) {
        return isMigrationRequiredForSyncMode(streamConfig.syncMode(), streamConfig.destinationSyncMode())
            && !doesValidV2RawTableAlreadyExist(streamConfig)
            && doesValidV1RawTableExist(convertToV1RawName(streamConfig));
    }

    default MigrationResult migrate(final SqlGenerator<DialectTableDefinition> sqlGenerator,
        final DestinationHandler<DialectTableDefinition> destinationHandler,
        final StreamConfig streamConfig) {
        final var migrateAndReset = String.join("\n",
            sqlGenerator.migrateFromV1toV2(streamConfig, convertToV1RawName(streamConfig)),
            sqlGenerator.softReset(streamConfig)
        );
        try {
            destinationHandler.execute(migrateAndReset);
        } catch (Exception e) {
            final var message = "Attempted and failed to migrate stream {}".formatted(streamConfig.id().finalName());
            throw new TableNotMigratedException(message, e);
        }
        return new MigrationResult(true);
    }


    default boolean doesV1RawTableMatchExpectedSchema(DialectTableDefinition existingV2AirbyteRawTable) {
        return schemaMatchesExpectation(existingV2AirbyteRawTable, RAW_TABLE_EXPECTED_V1_COLUMNS);
    }

    default boolean doesAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(DialectTableDefinition existingV2AirbyteRawTable) {
        if (!schemaMatchesExpectation(existingV2AirbyteRawTable, RAW_TABLE_EXPECTED_V2_COLUMNS)) {
            throw new UnexpectedSchemaException("Destination V2 Raw Table does not match expected Schema");
        } else {
            return true;
        }
    }

    default boolean isMigrationRequiredForSyncMode(final SyncMode syncMode, final DestinationSyncMode destinationSyncMode) {
        return !(SyncMode.FULL_REFRESH.equals(syncMode) && DestinationSyncMode.OVERWRITE.equals(destinationSyncMode));
    }

    default boolean doesValidV2RawTableAlreadyExist(final StreamConfig streamConfig) {
        if (doesAirbyteInternalNamespaceExist(streamConfig)) {
            final var existingV2Table = getTableIfExists(
                new AirbyteStreamNameNamespacePair(streamConfig.id().rawNamespace(), streamConfig.id().rawName()));
            return existingV2Table.isPresent() && doesAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(existingV2Table.get());
        }
        return false;
    }

    default boolean doesValidV1RawTableExist(AirbyteStreamNameNamespacePair rawTableNamePair) {
        final var existingV1RawTable = getTableIfExists(rawTableNamePair);
        return existingV1RawTable.isPresent() && doesV1RawTableMatchExpectedSchema(existingV1RawTable.get());
    }

    boolean doesAirbyteInternalNamespaceExist(StreamConfig streamConfig);

    boolean schemaMatchesExpectation(DialectTableDefinition existingTable, Collection<String> column);

    Optional<DialectTableDefinition> getTableIfExists(AirbyteStreamNameNamespacePair nameAndNamespacePair);

    AirbyteStreamNameNamespacePair convertToV1RawName(StreamConfig streamConfig);
}
