/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.direct_load_table.migrations

import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch

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
) : DirectLoadTableTempTableNameMigration {
    override suspend fun execute(names: TableCatalog) {
        val oldTempNameToNewTempName =
            names
                .map { (_, tableNameInfo) ->
                    val realTableName = tableNameInfo.tableNames.finalTableName!!
                    val oldTempTableName = realTableName.asOldStyleTempTable()
                    val newTempTableName = realTableName.asTempTable()
                    oldTempTableName to newTempTableName
                }
                .toMap()
        val existingOldTempTables =
            tableExistenceChecker.listExistingTables(oldTempNameToNewTempName.keys)
        coroutineScope {
            for (oldTempTableName in existingOldTempTables) {
                launch {
                    val realTableName = oldTempNameToNewTempName[oldTempTableName]!!
                    val tempTableName = realTableName.asTempTable()
                    sqlTableOperations.overwriteTable(oldTempTableName, tempTableName)
                }
            }
        }
    }
}

interface DirectLoadTableExistenceChecker {
    fun listExistingTables(tables: Collection<TableName>): Collection<TableName>
}
