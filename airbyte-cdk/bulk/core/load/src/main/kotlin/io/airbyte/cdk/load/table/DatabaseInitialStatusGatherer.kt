/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.table

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.table.directload.DirectLoadInitialStatus
import io.airbyte.cdk.load.table.directload.DirectLoadTableStatus
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch

interface DatabaseInitialStatus

/**
 * Some destinations can efficiently fetch multiple tables' information in a single query, so this
 * interface accepts multiple streams in a single method call.
 *
 * For destinations which do not support that optimization, a simpler implementation would be
 * something like this:
 * ```kotlin
 * streams.forEach { (stream, (tableNames, columnNames)) ->
 *   launch {
 *     // ... gather state...
 *   }
 * }
 * ```
 */
fun interface DatabaseInitialStatusGatherer<InitialStatus : DatabaseInitialStatus> {
    suspend fun gatherInitialStatus(): Map<DestinationStream, InitialStatus>
}

abstract class BaseDirectLoadInitialStatusGatherer(
    private val tableOperationsClient: TableOperationsClient,
    private val catalog: DestinationCatalog,
) : DatabaseInitialStatusGatherer<DirectLoadInitialStatus> {
    override suspend fun gatherInitialStatus(): Map<DestinationStream, DirectLoadInitialStatus> {
        val map =
            ConcurrentHashMap<DestinationStream, DirectLoadInitialStatus>(catalog.streams.size)
        coroutineScope {
            catalog.streams.forEach { s ->
                launch {
                    val tableNames = s.tableSchema.tableNames
                    map[s] = getInitialStatus(tableNames)
                }
            }
        }
        return map
    }

    private suspend fun getTableStatus(tableName: TableName): DirectLoadTableStatus? {
        val numberOfRecords: Long? = tableOperationsClient.countTable(tableName)
        return when (numberOfRecords) {
            // Missing table
            null -> null
            // Empty Table
            0L -> DirectLoadTableStatus(isEmpty = true)
            // Non-empty Table
            else -> DirectLoadTableStatus(isEmpty = false)
        }
    }

    private suspend fun getInitialStatus(names: TableNames): DirectLoadInitialStatus {
        return DirectLoadInitialStatus(
            realTable = getTableStatus(names.finalTableName!!),
            tempTable = getTableStatus(names.tempTableName!!),
        )
    }
}
