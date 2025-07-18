/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.typededupe

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.databricks.DatabricksConnectorClientsFactory
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksNamingTransformer
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksSqlGenerator
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import java.nio.file.Path
import java.sql.Connection
import java.sql.ResultSet
import java.util.Locale
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

abstract class AbstractDatabricksTypingDedupingTest(
    private val jdbcDatabase: JdbcDatabase,
    private val baseConfig: JsonNode,
) : BaseTypingDedupingTest() {
    override val imageName: String
        get() = "airbyte/destination-databricks:dev"
    private val connectorConfig: DatabricksConnectorConfig
        get() {
            return DatabricksConnectorConfig.deserialize(config!!)
        }

    companion object {
        fun setupDatabase(connectorConfigPath: String): Pair<JdbcDatabase, JsonNode> {
            val jsonConfig = Jsons.deserialize(IOs.readFile(Path.of(connectorConfigPath)))
            val connectorConfig = DatabricksConnectorConfig.deserialize(jsonConfig)

            val jdbcDatabase =
                DefaultJdbcDatabase(
                    DatabricksConnectorClientsFactory.createDataSource(connectorConfig)
                )
            // This will trigger warehouse start
            jdbcDatabase.execute("SELECT 1")

            return Pair(jdbcDatabase, jsonConfig)
        }
    }

    override fun generateConfig(): JsonNode {
        // Randomize the default namespace to avoid collisions between
        // concurrent test runs.
        val uniqueSuffix = RandomStringUtils.randomAlphabetic(10).lowercase(Locale.getDefault())
        val defaultSchema = "typing_deduping_default_schema_$uniqueSuffix"
        val deepCopy = baseConfig.deepCopy<ObjectNode>()
        (deepCopy as ObjectNode).put("schema", defaultSchema)
        // This method is called in BeforeEach so setup any other references needed per test
        return deepCopy
    }

    private fun rawTableIdentifier(
        streamNamespace: String?,
        streamName: String,
        suffix: String = ""
    ): String {
        val rawTableName =
            StreamId.concatenateRawTableName(streamNamespace ?: connectorConfig.schema, streamName)
        val rawTableSchema: String = JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
        return "`$rawTableSchema`.`$rawTableName$suffix`"
    }

    override fun dumpRawTableRecords(streamNamespace: String?, streamName: String): List<JsonNode> {
        return dumpTable(rawTableIdentifier(streamNamespace, streamName))
    }

    override fun dumpFinalTableRecords(
        streamNamespace: String?,
        streamName: String
    ): List<JsonNode> {
        return dumpTable("`${streamNamespace ?: connectorConfig.schema}`.`$streamName`")
    }

    private fun dumpTable(tableIdentifier: String): List<JsonNode> {
        return jdbcDatabase.bufferedResultSetQuery<JsonNode>(
            { connection: Connection ->
                connection
                    .createStatement()
                    .executeQuery(
                        """
                        SELECT *
                        FROM `${connectorConfig.database}`.$tableIdentifier
                        ORDER BY ${JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT} ASC
                    """.trimIndent(),
                    )
            },
            { resultSet: ResultSet ->
                JdbcSourceOperations()
                    .rowToJson(
                        resultSet,
                    )
            },
        )
    }

    override fun teardownStreamAndNamespace(streamNamespace: String?, streamName: String) {
        val finalSchema = streamNamespace ?: connectorConfig.schema
        // Clean up raw tables in airbyte_internal
        jdbcDatabase.execute(
            " DROP TABLE IF EXISTS `${connectorConfig.database}`.${
                rawTableIdentifier(
                    streamNamespace,
                    streamName,
                )
            }",
        )
        // Clean up volumes in airbyte_internal
        jdbcDatabase.execute(
            "DROP VOLUME IF EXISTS `${connectorConfig.database}`.${rawTableIdentifier(streamNamespace, streamName, "_staging")}"
        )

        // Clean up final schema completely.
        jdbcDatabase.execute(
            "DROP SCHEMA IF EXISTS `${connectorConfig.database}`.`$finalSchema` CASCADE"
        )
    }

    override val sqlGenerator: SqlGenerator
        get() = DatabricksSqlGenerator(DatabricksNamingTransformer(), connectorConfig.database)

    // Disabling until we can safely fetch generation ID
    @Test
    @Disabled
    override fun interruptedOverwriteWithoutPriorData() {
        super.interruptedOverwriteWithoutPriorData()
    }
}
