package io.airbyte.integrations.destination.databricks.sql

import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId

interface SqlOperations<T> {
    fun prepare(destinationInitialStatus: DestinationInitialStatus<T>): Result<Unit>
    fun copyIntoTableFromStage(stageId: String, streamId: StreamId): Result<Unit>
    fun updateFinalTable(streamConfig: StreamConfig): Result<Unit>

}
