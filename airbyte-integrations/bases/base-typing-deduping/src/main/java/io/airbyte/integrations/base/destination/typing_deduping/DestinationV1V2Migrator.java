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

    /**
     * This is the primary entrypoint to this interface
     * <p>
     * Determine whether a migration is necessary for a given stream and if so, migrate the raw table and rebuild the final table with a soft reset
     *
     * @param sqlGenerator       the class to use to generate sql
     * @param destinationHandler the handler to execute the sql statements
     * @param streamConfig       the stream to assess migration needs
     * @return an optional MigrationResult if a migration occurred
     */
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

    /**
     * Determine whether a given stream needs to be migrated from v1 to v2
     *
     * @param streamConfig the stream in question
     * @return whether to migrate the stream
     */
    default boolean shouldMigrate(final StreamConfig streamConfig) {
        return isMigrationRequiredForSyncMode(streamConfig.syncMode(), streamConfig.destinationSyncMode())
            && !doesValidV2RawTableAlreadyExist(streamConfig)
            && doesValidV1RawTableExist(convertToV1RawName(streamConfig));
    }

    /**
     * Execute sql statements that converts a v1 raw table to a v2 raw table. Leaves the v1 raw table intact
     *
     * @param sqlGenerator       the class which generates dialect specific sql statements
     * @param destinationHandler the class which executes the sql statements
     * @param streamConfig       the stream to migrate the raw table of
     * @return a successful migration result
     */
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
            final var message = "Attempted and failed to migrate stream %s".formatted(streamConfig.id().finalName());
            throw new TableNotMigratedException(message, e);
        }
        return new MigrationResult(true);
    }


    /**
     * Checks the schema of the v1 raw table to ensure it matches the expected format
     *
     * @param existingV2AirbyteRawTable the v1 raw table
     * @return whether the schema is as expected
     */
    default boolean doesV1RawTableMatchExpectedSchema(DialectTableDefinition existingV2AirbyteRawTable) {
        return schemaMatchesExpectation(existingV2AirbyteRawTable, RAW_TABLE_EXPECTED_V1_COLUMNS);
    }

    /**
     * Checks the schema of the v2 raw table to ensure it matches the expected format
     *
     * @param existingV2AirbyteRawTable the v2 raw table
     * @return whether the schema is as expected, if it exists and doesn't match then we're in an unrecoverable state.
     */
    default boolean doesAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(DialectTableDefinition existingV2AirbyteRawTable) {
        if (!schemaMatchesExpectation(existingV2AirbyteRawTable, RAW_TABLE_EXPECTED_V2_COLUMNS)) {
            throw new UnexpectedSchemaException("Destination V2 Raw Table does not match expected Schema");
        } else {
            return true;
        }
    }

    /**
     * If the sync mode is a full refresh and we overwrite the table then there is no need to migrate
     *
     * @param syncMode            stream sync mode
     * @param destinationSyncMode destination sync mode
     * @return whether this is full refresh overwrite
     */
    default boolean isMigrationRequiredForSyncMode(final SyncMode syncMode, final DestinationSyncMode destinationSyncMode) {
        return !(SyncMode.FULL_REFRESH.equals(syncMode) && DestinationSyncMode.OVERWRITE.equals(destinationSyncMode));
    }

    /**
     * Checks if a valid destinations v2 raw table already exists
     *
     * @param streamConfig the raw table to check
     * @return whether it exists and is in the correct format
     */
    default boolean doesValidV2RawTableAlreadyExist(final StreamConfig streamConfig) {
        if (doesAirbyteInternalNamespaceExist(streamConfig)) {
            final var existingV2Table = getTableIfExists(
                new AirbyteStreamNameNamespacePair(streamConfig.id().rawNamespace(), streamConfig.id().rawName()));
            return existingV2Table.isPresent() && doesAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(existingV2Table.get());
        }
        return false;
    }

    /**
     * Checks if a valid v1 raw table already exists
     *
     * @param rawTableNamePair the raw table to check
     * @return whether it exists and is in the correct format
     */
    default boolean doesValidV1RawTableExist(AirbyteStreamNameNamespacePair rawTableNamePair) {
        final var existingV1RawTable = getTableIfExists(rawTableNamePair);
        return existingV1RawTable.isPresent() && doesV1RawTableMatchExpectedSchema(existingV1RawTable.get());
    }

    /**
     * Checks to see if Airbyte's internal schema for destinations v2 exists
     *
     * @param streamConfig the stream to check
     * @return whether the schema exists
     */
    boolean doesAirbyteInternalNamespaceExist(StreamConfig streamConfig);

    /**
     * Checks a Table's schema and compares it to an expected schema to make sure it matches
     *
     * @param existingTable the table to check
     * @param columns       the expected schema
     * @return whether the existing table schema matches the expectation
     */
    boolean schemaMatchesExpectation(DialectTableDefinition existingTable, Collection<String> columns);

    /**
     * Get a reference ta a table if it exists
     *
     * @param nameAndNamespacePair the table to be accessed
     * @return an optional potentially containing a reference to the table
     */
    Optional<DialectTableDefinition> getTableIfExists(AirbyteStreamNameNamespacePair nameAndNamespacePair);

    /**
     * We use different naming conventions for raw table names in destinations v2, we need a way to map that back to v1 names
     *
     * @param streamConfig the stream in question
     * @return the valid v1 name and namespace for the same stream
     */
    AirbyteStreamNameNamespacePair convertToV1RawName(StreamConfig streamConfig);
}
