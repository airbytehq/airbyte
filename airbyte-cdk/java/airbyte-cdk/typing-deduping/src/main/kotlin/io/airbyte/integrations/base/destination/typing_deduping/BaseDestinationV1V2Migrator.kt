/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*

private val LOGGER = KotlinLogging.logger {}

abstract class BaseDestinationV1V2Migrator<DialectTableDefinition> : DestinationV1V2Migrator {
    @Throws(Exception::class)
    override fun migrateIfNecessary(
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<*>,
        streamConfig: StreamConfig
    ) {
        LOGGER.info {
            "Assessing whether migration is necessary for stream ${streamConfig.id.finalName}"
        }

        if (shouldMigrate(streamConfig)) {
            LOGGER.info { "Starting v2 Migration for stream ${streamConfig.id.finalName}" }
            migrate(sqlGenerator, destinationHandler, streamConfig)
            LOGGER.info {
                "V2 Migration completed successfully for stream ${streamConfig.id.finalName}"
            }
        } else {
            LOGGER.info { "No Migration Required for stream: ${streamConfig.id.finalName}" }
        }
    }

    /**
     * Determine whether a given stream needs to be migrated from v1 to v2
     *
     * @param streamConfig the stream in question
     * @return whether to migrate the stream
     */
    @Throws(Exception::class)
    fun shouldMigrate(streamConfig: StreamConfig): Boolean {
        val v1RawTable = convertToV1RawName(streamConfig)
        LOGGER.info {
            "Checking whether v1 raw table ${v1RawTable.tableName} in dataset ${v1RawTable.namespace} exists"
        }
        val syncModeNeedsMigration =
            isMigrationRequiredForSyncMode(streamConfig.destinationSyncMode)
        val noValidV2RawTableExists = !doesValidV2RawTableAlreadyExist(streamConfig)
        val aValidV1RawTableExists =
            doesValidV1RawTableExist(v1RawTable.namespace, v1RawTable.tableName)
        LOGGER.info {
            "Migration Info: Required for Sync mode: $syncModeNeedsMigration, " +
                "No existing v2 raw tables: $noValidV2RawTableExists, " +
                "A v1 raw table exists: $aValidV1RawTableExists"
        }
        return syncModeNeedsMigration && noValidV2RawTableExists && aValidV1RawTableExists
    }

    /**
     * Execute sql statements that converts a v1 raw table to a v2 raw table. Leaves the v1 raw
     * table intact
     *
     * @param sqlGenerator the class which generates dialect specific sql statements
     * @param destinationHandler the class which executes the sql statements
     * @param streamConfig the stream to migrate the raw table of
     */
    @Throws(TableNotMigratedException::class)
    fun migrate(
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<*>,
        streamConfig: StreamConfig
    ) {
        val namespacedTableName = convertToV1RawName(streamConfig)
        try {
            destinationHandler.execute(
                sqlGenerator.migrateFromV1toV2(
                    streamConfig.id,
                    namespacedTableName.namespace,
                    namespacedTableName.tableName
                )
            )
        } catch (e: Exception) {
            val message = "Attempted and failed to migrate stream ${streamConfig.id.finalName}"
            throw TableNotMigratedException(message, e)
        }
    }

    /**
     * Checks the schema of the v1 raw table to ensure it matches the expected format
     *
     * @param existingV2AirbyteRawTable the v1 raw table
     * @return whether the schema is as expected
     */
    private fun doesV1RawTableMatchExpectedSchema(
        existingV2AirbyteRawTable: DialectTableDefinition
    ): Boolean {
        return schemaMatchesExpectation(
            existingV2AirbyteRawTable,
            JavaBaseConstants.LEGACY_RAW_TABLE_COLUMNS
        )
    }

    /**
     * Checks the schema of the v2 raw table to ensure it matches the expected format
     *
     * @param existingV2AirbyteRawTable the v2 raw table
     */
    private fun validateAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(
        existingV2AirbyteRawTable: DialectTableDefinition
    ) {
        // Account for the fact that the meta column was added later, so skip the rebuilding of the
        // raw
        // table.
        if (
            !(schemaMatchesExpectation(
                existingV2AirbyteRawTable,
                JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES_WITHOUT_META,
            ) ||
                schemaMatchesExpectation(
                    existingV2AirbyteRawTable,
                    JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES,
                ) ||
                schemaMatchesExpectation(
                    existingV2AirbyteRawTable,
                    JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES_WITH_GENERATION,
                ))
        ) {
            throw UnexpectedSchemaException(
                "Destination V2 Raw Table does not match expected Schema",
            )
        }
    }

    /**
     * If the sync mode is a full refresh and we overwrite the table then there is no need to
     * migrate
     *
     * @param destinationSyncMode destination sync mode
     * @return whether this is full refresh overwrite
     */
    private fun isMigrationRequiredForSyncMode(destinationSyncMode: DestinationSyncMode?): Boolean {
        return DestinationSyncMode.OVERWRITE != destinationSyncMode
    }

    /**
     * Checks if a valid destinations v2 raw table already exists
     *
     * @param streamConfig the raw table to check
     * @return whether it exists and is in the correct format
     */
    @Throws(Exception::class)
    private fun doesValidV2RawTableAlreadyExist(streamConfig: StreamConfig): Boolean {
        if (doesAirbyteInternalNamespaceExist(streamConfig)) {
            val existingV2Table =
                getTableIfExists(streamConfig.id.rawNamespace, streamConfig.id.rawName)
            existingV2Table.ifPresent { existingV2AirbyteRawTable: DialectTableDefinition ->
                this.validateAirbyteInternalNamespaceRawTableMatchExpectedV2Schema(
                    existingV2AirbyteRawTable
                )
            }
            return existingV2Table.isPresent
        }
        return false
    }

    /**
     * Checks if a valid v1 raw table already exists
     *
     * @param namespace
     * @param tableName
     * @return whether it exists and is in the correct format
     */
    @Throws(Exception::class)
    protected open fun doesValidV1RawTableExist(namespace: String?, tableName: String?): Boolean {
        val existingV1RawTable = getTableIfExists(namespace, tableName)
        return existingV1RawTable.isPresent &&
            doesV1RawTableMatchExpectedSchema(existingV1RawTable.get())
    }

    /**
     * Checks to see if Airbyte's internal schema for destinations v2 exists
     *
     * @param streamConfig the stream to check
     * @return whether the schema exists
     */
    @Throws(Exception::class)
    abstract fun doesAirbyteInternalNamespaceExist(streamConfig: StreamConfig?): Boolean

    /**
     * Checks a Table's schema and compares it to an expected schema to make sure it matches
     *
     * @param existingTable the table to check
     * @param columns the expected schema
     * @return whether the existing table schema matches the expectation
     */
    abstract fun schemaMatchesExpectation(
        existingTable: DialectTableDefinition,
        columns: Collection<String>
    ): Boolean

    /**
     * Get a reference ta a table if it exists
     *
     * @param namespace
     * @param tableName
     * @return an optional potentially containing a reference to the table
     */
    @Throws(Exception::class)
    abstract fun getTableIfExists(
        namespace: String?,
        tableName: String?
    ): Optional<DialectTableDefinition>

    /**
     * We use different naming conventions for raw table names in destinations v2, we need a way to
     * map that back to v1 names
     *
     * @param streamConfig the stream in question
     * @return the valid v1 name and namespace for the same stream
     */
    abstract fun convertToV1RawName(streamConfig: StreamConfig): NamespacedTableName
}
