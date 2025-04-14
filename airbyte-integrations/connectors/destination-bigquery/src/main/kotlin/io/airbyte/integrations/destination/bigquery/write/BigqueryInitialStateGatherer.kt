package io.airbyte.integrations.destination.bigquery.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.DestinationInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.TableNames
import io.airbyte.cdk.load.orchestration.legacy_typing_deduping.TypingDedupingDestinationInitialStatus

class BigqueryInitialStateGatherer : DestinationInitialStatusGatherer<TypingDedupingDestinationInitialStatus> {
    override fun gatherInitialStatus(streams: Map<DestinationStream, Pair<TableNames, ColumnNameMapping>>): Map<DestinationStream, TypingDedupingDestinationInitialStatus> {
        TODO("Not yet implemented")
    }
}
