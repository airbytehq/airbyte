/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.check

import io.airbyte.cdk.load.check.DestinationCheckerV2
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.SnowflakeSqlNameTransformer
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeInsertBuffer
import jakarta.inject.Singleton
import java.util.UUID
import kotlinx.coroutines.runBlocking

@Singleton
class SnowflakeChecker(
    private val snowflakeAirbyteClient: SnowflakeAirbyteClient,
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val snowflakeSqlNameTransformer: SnowflakeSqlNameTransformer,
) : DestinationCheckerV2 {

    override fun check() {
        val columnName = "testKey"
        val data = mapOf(columnName to AirbyteValue.from("test-value"))
        val outputSchema = snowflakeSqlNameTransformer.transform(snowflakeConfiguration.schema)
        val tableName =
            snowflakeSqlNameTransformer.transform(
                "_airbyte_connection_test_${
                UUID.randomUUID().toString().replace("-".toRegex(), "")}"
            )
        val qualifiedTableName = TableName(namespace = outputSchema, name = tableName)
        val destinationStream =
            DestinationStream(
                unmappedNamespace = outputSchema,
                unmappedName = tableName,
                importType = Append,
                schema =
                    ObjectType(linkedMapOf(columnName to FieldType(StringType, nullable = false))),
                generationId = 0L,
                minimumGenerationId = 0L,
                syncId = 0L,
                namespaceMapper = NamespaceMapper()
            )
        val snowflakeInsertBuffer =
            SnowflakeInsertBuffer(
                tableName = qualifiedTableName,
                snowflakeClient = snowflakeAirbyteClient
            )

        runBlocking {
            try {
                snowflakeAirbyteClient.createNamespace(outputSchema)
                snowflakeAirbyteClient.createSnowflakeStage(qualifiedTableName)
                snowflakeAirbyteClient.createTable(
                    stream = destinationStream,
                    tableName = qualifiedTableName,
                    columnNameMapping = ColumnNameMapping(emptyMap()),
                    replace = true,
                )

                snowflakeInsertBuffer.accumulate(data)
                snowflakeInsertBuffer.flush()

                val tableCount = snowflakeAirbyteClient.countTable(qualifiedTableName)
                require(tableCount == 1L) {
                    "Failed to insert expected rows into check table. Actual written: $tableCount"
                }
            } finally {
                snowflakeAirbyteClient.dropTable(qualifiedTableName)
            }
        }
    }
}
