package io.airbyte.integrations.destination.databricks.sql

import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState

class DatabricksDestinationHandler : DestinationHandler<MinimumDestinationState.Impl> {
    override fun execute(sql: Sql) {
        TODO("Not yet implemented")
    }

    override fun gatherInitialState(streamConfigs: List<StreamConfig>): List<DestinationInitialStatus<MinimumDestinationState.Impl>> {
        TODO("Not yet implemented")
    }

    override fun commitDestinationStates(destinationStates: Map<StreamId, MinimumDestinationState.Impl>) {
        TODO("Not yet implemented")
    }
}
