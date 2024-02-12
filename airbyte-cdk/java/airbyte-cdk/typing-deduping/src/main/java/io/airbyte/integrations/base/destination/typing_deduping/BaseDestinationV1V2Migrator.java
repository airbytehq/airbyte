/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.LEGACY_RAW_TABLE_COLUMNS;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES;

import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.Collection;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseDestinationV1V2Migrator<DialectTableDefinition> implements DestinationV1V2Migrator<DialectTableDefinition> {

  protected static final Logger LOGGER = LoggerFactory.getLogger(BaseDestinationV1V2Migrator.class);

  @Override
  public void migrateIfNecessary(
                                 final SqlGenerator<DialectTableDefinition> sqlGenerator,
                                 final DestinationHandler<DialectTableDefinition> destinationHandler,
                                 final StreamConfig streamConfig)
      throws Exception {
    LOGGER.info("Assessing whether migration is necessary for stream {}", streamConfig.id().finalName());
    if (shouldMigrate(streamConfig)) {
      LOGGER.info("Starting v2 Migration for stream {}", streamConfig.id().finalName());
      migrate(sqlGenerator, destinationHandler, streamConfig);
      LOGGER.info("V2 Migration completed successfully for stream {}", streamConfig.id().finalName());
    } else {
      LOGGER.info("No Migration Required for stream: {}", streamConfig.id().finalName());
    }

  }

  /**
   * Determine whether a given stream needs to be migrated from v1 to v2
   *
   * @param streamConfig the stream in question
   * @return whether to migrate the stream
   */
  protected boolean shouldMigrate(final StreamConfig streamConfig) throws Exception {
    final var v1RawTable = convertToV1RawName(streamConfig);
    LOGGER.info("Checking whether v1 raw table {} in dataset {} exists", v1RawTable.tableName(), v1RawTable.namespace());
    final var syncModeNeedsMigration = isMigrationRequiredForSyncMode(streamConfig.destinationSyncMode());
    final var noValidV2RawTableExists = !doesValidV2RawTableAlreadyExist(streamConfig);
    final var aValidV1RawTableExists = doesValidV1RawTableExist(v1RawTable.namespace(), v1RawTable.tableName());
    LOGGER.info("Migration Info: Required for Sync mode: {}, No existing v2 raw tables: {}, A v1 raw table exists: {}",
        syncModeNeedsMigration, noValidV2RawTableExists, aValidV1RawTableExists);
    return syncModeNeedsMigration && noValidV2RawTableExists && aValidV1RawTableExists;
  }

  /**
   * Execute sql statements that converts a v1 raw table to a v2 raw table. Leaves the v1 raw table
   * intact
   *
   * @param sqlGenerator the class which generates dialect specific sql statements
   * @param destinationHandler the class which executes the sql statements
   * @param streamConfig the stream to migrate the raw table of
   */
  public void migrate(final SqlGenerator<DialectTableDefinition> sqlGenerator,
                      final DestinationHandler<DialectTableDefinition> destinationHandler,
                      final StreamConfig streamConfig)
      throws TableNotMigratedException {
    final var namespacedTableName = convertToV1RawName(streamConfig);
    try {
      destinationHandler.execute(sqlGenerator.migrateFromV1toV2(streamConfig.id(), namespacedTableName.namespace(), namespacedTableName.tableName()));
    } catch (final Exception e) {
      final var message = "Attempted and failed to migrate stream %s".formatted(streamConfig.id().finalName());
      throw new TableNotMigratedException(message, e);
    }
  }

  /**
   * Checks the schema of the v1 raw table to ensure it matches the expected format
   *
   * @param existingV2AirbyteRawTable the v1 raw table
   * @return whether the schema is as expected
   */
  private boolean doesV1RawTableMatchExpectedSchema(final DialectTableDefinition existingV2AirbyteRawTable) {

    return schemaMatchesExpectation(existingV2AirbyteRawTable, LEGACY_RAW_TABLE_COLUMNS);
  }

  /**
   * Checks the schema of the v2 raw table to ensure it matches the expected format
   *
   * @param existingV2AirbyteRawTable the v2 raw table
   */
  private void validateAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(final DialectTableDefinition existingV2AirbyteRawTable) {
    if (!schemaMatchesExpectation(existingV2AirbyteRawTable, V2_RAW_TABLE_COLUMN_NAMES)) {
      throw new UnexpectedSchemaException("Destination V2 Raw Table does not match expected Schema");
    }
  }

  /**
   * If the sync mode is a full refresh and we overwrite the table then there is no need to migrate
   *
   * @param destinationSyncMode destination sync mode
   * @return whether this is full refresh overwrite
   */
  private boolean isMigrationRequiredForSyncMode(final DestinationSyncMode destinationSyncMode) {
    return !DestinationSyncMode.OVERWRITE.equals(destinationSyncMode);
  }

  /**
   * Checks if a valid destinations v2 raw table already exists
   *
   * @param streamConfig the raw table to check
   * @return whether it exists and is in the correct format
   */
  private boolean doesValidV2RawTableAlreadyExist(final StreamConfig streamConfig) throws Exception {
    if (doesAirbyteInternalNamespaceExist(streamConfig)) {
      final var existingV2Table = getTableIfExists(streamConfig.id().rawNamespace(), streamConfig.id().rawName());
      existingV2Table.ifPresent(this::validateAirbyteInternalNamespaceRawTableMatchExpectedV2Schema);
      return existingV2Table.isPresent();
    }
    return false;
  }

  /**
   * Checks if a valid v1 raw table already exists
   *
   * @param namespace
   * @param tableName
   * @return whether it exists and is in the correct format
   */
  protected boolean doesValidV1RawTableExist(final String namespace, final String tableName) throws Exception {
    final var existingV1RawTable = getTableIfExists(namespace, tableName);
    return existingV1RawTable.isPresent() && doesV1RawTableMatchExpectedSchema(existingV1RawTable.get());
  }

  /**
   * Checks to see if Airbyte's internal schema for destinations v2 exists
   *
   * @param streamConfig the stream to check
   * @return whether the schema exists
   */
  abstract protected boolean doesAirbyteInternalNamespaceExist(StreamConfig streamConfig) throws Exception;

  /**
   * Checks a Table's schema and compares it to an expected schema to make sure it matches
   *
   * @param existingTable the table to check
   * @param columns the expected schema
   * @return whether the existing table schema matches the expectation
   */
  abstract protected boolean schemaMatchesExpectation(DialectTableDefinition existingTable, Collection<String> columns);

  /**
   * Get a reference ta a table if it exists
   *
   * @param namespace
   * @param tableName
   * @return an optional potentially containing a reference to the table
   */
  abstract protected Optional<DialectTableDefinition> getTableIfExists(String namespace, String tableName) throws Exception;

  /**
   * We use different naming conventions for raw table names in destinations v2, we need a way to map
   * that back to v1 names
   *
   * @param streamConfig the stream in question
   * @return the valid v1 name and namespace for the same stream
   */
  abstract protected NamespacedTableName convertToV1RawName(StreamConfig streamConfig);

}
