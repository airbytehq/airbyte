package io.airbyte.integrations.destination.databricks.staging

import com.databricks.sdk.WorkspaceClient
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import java.io.InputStream

class DatabricksStagingOperations(val workspaceClient: WorkspaceClient) : StagingOperations {

    override fun create(streamId: StreamId): Result<Unit> {
        TODO("Not yet implemented")
    }

    override fun upload(streamId: StreamId, contents: InputStream): Result<String> {
        TODO("Not yet implemented")
    }

    override fun delete(streamId: StreamId): Result<Unit> {
        TODO("Not yet implemented")
    }


}
