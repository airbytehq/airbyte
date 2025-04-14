/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration

import io.airbyte.cdk.load.command.DestinationStream

interface DestinationInitialStatus

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
fun interface DestinationInitialStatusGatherer<InitialStatus : DestinationInitialStatus> {
    suspend fun gatherInitialStatus(
        streams: Map<DestinationStream, Pair<TableNames, ColumnNameMapping>>,
    ): Map<DestinationStream, InitialStatus>
}
