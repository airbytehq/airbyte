package io.airbyte.integrations.destination.databricks.sql

import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId

interface SqlOperations {
    fun prepare(streamConfig: StreamConfig): Result<Unit>
    fun copyIntoTableFromStage(stageId: String, streamId: StreamId): Result<Unit>
    fun updateFinalTable(streamConfig: StreamConfig): Result<Unit>

}
