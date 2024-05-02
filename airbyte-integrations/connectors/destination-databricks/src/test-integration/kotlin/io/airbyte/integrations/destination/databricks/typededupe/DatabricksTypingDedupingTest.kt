package io.airbyte.integrations.destination.databricks.typededupe

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import org.junit.jupiter.api.Disabled

@Disabled
class DatabricksTypingDedupingTest : BaseTypingDedupingTest() {
    override val imageName: String
        get() = TODO("Not yet implemented")

    override fun generateConfig(): JsonNode? {
        TODO("Not yet implemented")
    }

    override fun dumpRawTableRecords(streamNamespace: String?, streamName: String): List<JsonNode> {
        TODO("Not yet implemented")
    }

    override fun dumpFinalTableRecords(
        streamNamespace: String?,
        streamName: String
    ): List<JsonNode> {
        TODO("Not yet implemented")
    }

    override fun teardownStreamAndNamespace(streamNamespace: String?, streamName: String) {
        TODO("Not yet implemented")
    }

    override val sqlGenerator: SqlGenerator
        get() = TODO("Not yet implemented")
}
