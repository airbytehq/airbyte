/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag.getRawNamespaceOverride
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.StreamId.Companion.concatenateRawTableName
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeSoftReset
import io.airbyte.integrations.base.destination.typing_deduping.V2TableMigrator
import io.airbyte.integrations.destination.snowflake.SnowflakeDestination
import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.sql.SQLException
import java.util.*
import kotlin.collections.LinkedHashMap
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class SnowflakeV2TableMigrator(
    private val database: JdbcDatabase,
    private val databaseName: String,
    private val generator: SnowflakeSqlGenerator,
    private val handler: SnowflakeDestinationHandler
) : V2TableMigrator {
    private val rawNamespace: String =
        getRawNamespaceOverride(SnowflakeDestination.RAW_SCHEMA_OVERRIDE)
            .orElse(JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE)

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    @Throws(Exception::class)
    override fun migrateIfNecessary(streamConfig: StreamConfig?) {
        val caseSensitiveStreamId =
            buildStreamId_caseSensitive(
                streamConfig!!.id.originalNamespace,
                streamConfig.id.originalName,
                rawNamespace
            )
        val syncModeRequiresMigration =
            streamConfig.destinationSyncMode != DestinationSyncMode.OVERWRITE
        val existingTableCaseSensitiveExists = findExistingTable(caseSensitiveStreamId).isPresent
        val existingTableUppercaseDoesNotExist = findExistingTable(streamConfig.id).isEmpty
        LOGGER.info(
            "Checking whether upcasing migration is necessary for {}.{}. Sync mode requires migration: {}; existing case-sensitive table exists: {}; existing uppercased table does not exist: {}",
            streamConfig.id.originalNamespace,
            streamConfig.id.originalName,
            syncModeRequiresMigration,
            existingTableCaseSensitiveExists,
            existingTableUppercaseDoesNotExist
        )
        if (
            syncModeRequiresMigration &&
                existingTableCaseSensitiveExists &&
                existingTableUppercaseDoesNotExist
        ) {
            LOGGER.info(
                "Executing upcasing migration for {}.{}",
                streamConfig.id.originalNamespace,
                streamConfig.id.originalName
            )
            executeSoftReset(generator, handler, streamConfig)
        }
    }

    @Throws(SQLException::class)
    private fun findExistingTable(id: StreamId): Optional<TableDefinition> {
        // The obvious database.getMetaData().getColumns() solution doesn't work, because JDBC
        // translates
        // VARIANT as VARCHAR
        val existingTableMap: LinkedHashMap<String, LinkedHashMap<String, TableDefinition>> =
            SnowflakeDestinationHandler.Companion.findExistingTables(
                database,
                databaseName,
                listOf(id)
            )
        if (
            existingTableMap.containsKey(id.finalNamespace) &&
                existingTableMap[id.finalNamespace]!!.containsKey(id.finalName)
        ) {
            return Optional.of(existingTableMap[id.finalNamespace]!![id.finalName]!!)
        }
        return Optional.empty()
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(SnowflakeV2TableMigrator::class.java)

        // These methods were copied from
        // https://github.com/airbytehq/airbyte/blob/d5fdb1b982d464f54941bf9a830b9684fb47d249/airbyte-integrations/connectors/destination-snowflake/src/main/java/io/airbyte/integrations/destination/snowflake/typing_deduping/SnowflakeSqlGenerator.java
        // which is the highest version of destination-snowflake that still uses
        // quoted+case-sensitive
        // identifiers
        private fun buildStreamId_caseSensitive(
            namespace: String,
            name: String,
            rawNamespaceOverride: String
        ): StreamId {
            // No escaping needed, as far as I can tell. We quote all our identifier names.
            return StreamId(
                escapeIdentifier_caseSensitive(namespace),
                escapeIdentifier_caseSensitive(name),
                escapeIdentifier_caseSensitive(rawNamespaceOverride),
                escapeIdentifier_caseSensitive(concatenateRawTableName(namespace, name)),
                namespace,
                name
            )
        }

        private fun escapeIdentifier_caseSensitive(identifier: String): String {
            // Note that we don't need to escape backslashes here!
            // The only special character in an identifier is the double-quote, which needs to be
            // doubled.
            return identifier.replace("\"", "\"\"")
        }
    }
}
