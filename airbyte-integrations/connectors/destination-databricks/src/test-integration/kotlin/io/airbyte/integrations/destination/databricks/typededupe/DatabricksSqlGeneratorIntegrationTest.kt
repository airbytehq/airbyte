package io.airbyte.integrations.destination.databricks.typededupe

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.integrations.base.destination.typing_deduping.BaseSqlGeneratorIntegrationTest
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import org.junit.jupiter.api.BeforeAll

class DatabricksSqlGeneratorIntegrationTest : BaseSqlGeneratorIntegrationTest<MinimumDestinationState>() {
    companion object {
        private lateinit var jdbcDatabase: JdbcDatabase;
        @JvmStatic
        @BeforeAll
        fun setupDatabase() {
            jdbcDatabase =
        }
    }

    override val destinationHandler: DestinationHandler<MinimumDestinationState>
        get() = TODO("Not yet implemented")
    override val sqlGenerator: SqlGenerator
        get() = TODO("Not yet implemented")


    override fun createNamespace(namespace: String?) {
        super.namespace
        TODO("Not yet implemented")
    }

    override fun createRawTable(streamId: StreamId) {
        TODO("Not yet implemented")
    }

    override fun createV1RawTable(v1RawTable: StreamId) {
        TODO("Not yet implemented")
    }

    override fun insertRawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        TODO("Not yet implemented")
    }

    override fun insertV1RawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        TODO("Not yet implemented")
    }

    override fun insertFinalTableRecords(
        includeCdcDeletedAt: Boolean,
        streamId: StreamId,
        suffix: String?,
        records: List<JsonNode>
    ) {
        TODO("Not yet implemented")
    }

    override fun dumpRawTableRecords(streamId: StreamId): List<JsonNode> {
        TODO("Not yet implemented")
    }

    override fun dumpFinalTableRecords(streamId: StreamId, suffix: String?): List<JsonNode> {
        TODO("Not yet implemented")
    }

    override fun teardownNamespace(namespace: String?) {
        TODO("Not yet implemented")
    }

    override fun testCreateTableIncremental() {
        TODO("Not yet implemented")
    }
}
