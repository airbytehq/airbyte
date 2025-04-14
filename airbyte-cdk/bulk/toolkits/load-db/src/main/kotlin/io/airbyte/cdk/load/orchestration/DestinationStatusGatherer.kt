package io.airbyte.cdk.load.orchestration

import io.airbyte.cdk.load.command.DestinationStream

interface DestinationInitialStatus

fun interface DestinationStatusGatherer<InitialStatus : DestinationInitialStatus> {
    fun gatherInitialStatus(
        streams: Map<DestinationStream, Pair<TableNames, ColumnNameMapping>>,
    ): Map<DestinationStream.Descriptor, InitialStatus>
}
