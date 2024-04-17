package io.airbyte.integrations.destination.databricks.staging

import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import java.io.InputStream

interface StagingOperations {

    fun create(streamId: StreamId): Result<Unit>
    fun upload(streamId: StreamId, contents: InputStream): Result<String>
    fun delete(streamId: StreamId): Result<Unit>
}
