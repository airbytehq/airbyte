/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.client

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.table.directload.DirectLoadInitialStatus
import io.airbyte.cdk.load.table.directload.DirectLoadTableStatus
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch

/**
 * Gathers initial table status for all streams in the catalog.
 *
 * Uses [RedshiftAirbyteClient.isTableNotEmpty] instead of the CDK's default [countTable] approach.
 * This replaces a full `COUNT(*)` table scan with a `SELECT EXISTS(... LIMIT 1)` query, which is
 * O(1) for non-empty tables — a significant performance improvement for large tables (e.g. billions
 * of rows: instant vs. potentially minutes).
 */
@Singleton
class RedshiftInitialStatusGatherer(
    private val client: RedshiftAirbyteClient,
    private val catalog: DestinationCatalog,
) : DatabaseInitialStatusGatherer<DirectLoadInitialStatus> {

    override suspend fun gatherInitialStatus(): Map<DestinationStream, DirectLoadInitialStatus> {
        val map =
            ConcurrentHashMap<DestinationStream, DirectLoadInitialStatus>(catalog.streams.size)
        coroutineScope {
            catalog.streams.forEach { stream ->
                launch {
                    val tableNames = stream.tableSchema.tableNames
                    map[stream] =
                        DirectLoadInitialStatus(
                            realTable = getTableStatus(tableNames.finalTableName!!),
                            tempTable = getTableStatus(tableNames.tempTableName!!),
                        )
                }
            }
        }
        return map
    }

    private suspend fun getTableStatus(tableName: TableName): DirectLoadTableStatus? {
        val notEmpty: Boolean? = client.isTableNotEmpty(tableName)
        return when (notEmpty) {
            // Table does not exist
            null -> null
            // Table exists — isEmpty is the inverse of notEmpty
            else -> DirectLoadTableStatus(isEmpty = !notEmpty)
        }
    }
}
