/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration

import io.airbyte.cdk.load.command.DestinationStream

interface DestinationInitialStatus

fun interface DestinationInitialStatusGatherer<InitialStatus : DestinationInitialStatus> {
    fun gatherInitialStatus(
        streams: Map<DestinationStream, Pair<TableNames, ColumnNameMapping>>,
    ): Map<DestinationStream, InitialStatus>
}
