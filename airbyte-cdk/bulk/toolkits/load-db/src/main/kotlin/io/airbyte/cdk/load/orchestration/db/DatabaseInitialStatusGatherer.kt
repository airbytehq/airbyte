/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db

import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
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
    suspend fun gatherInitialStatus(streams: TableCatalog): Map<DestinationStream, InitialStatus>
}

abstract class BaseDirectLoadInitialStatusGatherer(
    private val airbyteClient: AirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DatabaseInitialStatusGatherer<DirectLoadInitialStatus> {
    override suspend fun gatherInitialStatus(
        streams: TableCatalog
    ): Map<DestinationStream, DirectLoadInitialStatus> {
        val map = ConcurrentHashMap<DestinationStream, DirectLoadInitialStatus>(streams.size)
        coroutineScope {
            streams.forEach { (stream, tableNameInfo) ->
                launch {
                    val tableName = tableNameInfo.tableNames.finalTableName!!
                    map[stream] = getInitialStatus(tableName)
                }
            }
        }
        return map
    }

    private suspend fun getTableStatus(tableName: TableName): DirectLoadTableStatus? {
        val numberOfRecords: Long? = airbyteClient.countTable(tableName)
        return when (numberOfRecords) {
            // Missing table
            null -> null
            // Empty Table
            0L -> DirectLoadTableStatus(isEmpty = true)
            // Non-empty Table
            else -> DirectLoadTableStatus(isEmpty = false)
        }
    }

    private suspend fun getInitialStatus(tableName: TableName): DirectLoadInitialStatus {
        return DirectLoadInitialStatus(
            realTable = getTableStatus(tableName),
            tempTable = getTableStatus(tempTableNameGenerator.generate(tableName)),
        )
    }
}
