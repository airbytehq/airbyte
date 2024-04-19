package io.airbyte.integrations.destination.databricks.typededupe

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.BaseSqlGeneratorIntegrationTest
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.databricks.ConnectorClientsFactory
import io.airbyte.integrations.destination.databricks.DatabricksNamingTransformer
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksDestinationHandler
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksSqlGenerator
import io.airbyte.integrations.destination.databricks.jdbc.DatabrickStorageOperations
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled

class DatabricksSqlGeneratorIntegrationTest : BaseSqlGeneratorIntegrationTest<MinimumDestinationState.Impl>() {
    companion object {
        private lateinit var jdbcDatabase: JdbcDatabase
        private lateinit var connectorConfig: DatabricksConnectorConfig
        @JvmStatic
        @BeforeAll
        fun setupDatabase() {
            val rawConfig = Files.readString(Path.of("secrets/new_config.json"))
            val connectorConfig = DatabricksConnectorConfig.deserialize(Jsons.deserialize(rawConfig))
            jdbcDatabase = DefaultJdbcDatabase(ConnectorClientsFactory.createDataSource(connectorConfig))
        }
    }

    override val destinationHandler: DestinationHandler<MinimumDestinationState.Impl>
        get() = DatabricksDestinationHandler(connectorConfig.database, jdbcDatabase, connectorConfig.rawSchemaOverride)
    override val sqlGenerator: SqlGenerator
        get() = DatabricksSqlGenerator(DatabricksNamingTransformer())
    val sqlOperations: DatabrickStorageOperations = DatabrickStorageOperations(sqlGenerator, destinationHandler)


    override fun createNamespace(namespace: String?) {
        sqlGenerator.createSchema(namespace)
    }

    override fun createRawTable(streamId: StreamId) {
        sqlOperations.createRawTable(streamId.rawNamespace!!, streamId.rawName!!)
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

    @Disabled
    override fun testCreateTableIncremental() {

    }

    @Disabled ("No V1 Table migration for databricks")
    override fun testV1V2migration() {

    }
}
