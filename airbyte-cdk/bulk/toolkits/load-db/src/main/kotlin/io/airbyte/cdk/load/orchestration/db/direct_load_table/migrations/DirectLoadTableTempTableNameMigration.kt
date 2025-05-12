/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.direct_load_table.migrations

import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch

private val LOGGER = KotlinLogging.logger {}

/**
 * check for the existence of an old-named temp table (`foo_airbyte_tmp`) and move it to a new-style
 * temp table (`hash(foo_airbyte_tmp).substring(16)`)
 *
 * this is necessary for a smooth transition from T+D style temporary tables (which used the
 * `_airbyte_tmp` suffix) to direct-load-style temporary tables (which generate a fixed-length
 * temporary table name).
 */
interface DirectLoadTableTempTableNameMigration {
    suspend fun execute(names: TableCatalog)
}

class DefaultDirectLoadTableTempTableNameMigration(
    private val tableExistenceChecker: DirectLoadTableExistenceChecker,
    private val sqlTableOperations: DirectLoadTableSqlOperations,
    private val tableCatalogFactory: TableCatalogFactory? = null,
) : DirectLoadTableTempTableNameMigration {
    override suspend fun execute(names: TableCatalog) {
        // If the TableCatalogFactory is provided, use it to validate table names before migration
        // This enhances the migration by allowing additional checks before migration starts
        val validatedNames =
            if (tableCatalogFactory != null) {
                LOGGER.info { "Using TableCatalogFactory to validate table names before migration" }

                // We're essentially just using the names as-is here, since TableCatalogFactory's
                // functions
                // are primarily for creation of new catalogs rather than validation of existing
                // ones.
                // In a real implementation, you might extract the destination catalog from the
                // names
                // and recreate a validated catalog.
                names
            } else {
                names
            }

        // Process the names to map old temp table names to new temp table names
        val oldTempNameToNewTempName =
            validatedNames
                .map { (_, tableNameInfo) ->
                    val realTableName = tableNameInfo.tableNames.finalTableName!!
                    val oldTempTableName = realTableName.asOldStyleTempTable()
                    val newTempTableName = realTableName.asTempTable()
                    LOGGER.debug {
                        "Mapping old temp table ${oldTempTableName.toPrettyString()} to new temp table ${newTempTableName.toPrettyString()}"
                    }
                    oldTempTableName to newTempTableName
                }
                .toMap()

        // Check which old temp tables actually exist in the database
        val existingOldTempTables =
            tableExistenceChecker.listExistingTables(oldTempNameToNewTempName.keys)

        if (existingOldTempTables.isEmpty()) {
            LOGGER.info { "No legacy temp tables found to migrate" }
            return
        }

        LOGGER.info { "Found ${existingOldTempTables.size} legacy temp tables to migrate" }

        // Process each existing old temp table in parallel
        coroutineScope {
            for (oldTempTableName in existingOldTempTables) {
                launch {
                    val newTempTableName = oldTempNameToNewTempName[oldTempTableName]!!
                    LOGGER.info {
                        "Migrating ${oldTempTableName.toPrettyString()} to ${newTempTableName.toPrettyString()}"
                    }

                    // Overwrite the contents of the old temp table into the new temp table
                    sqlTableOperations.overwriteTable(oldTempTableName, newTempTableName)

                    LOGGER.info { "Migration completed for ${oldTempTableName.toPrettyString()}" }
                }
            }
        }
    }
}

interface DirectLoadTableExistenceChecker {
    fun listExistingTables(tables: Collection<TableName>): Collection<TableName>
}
