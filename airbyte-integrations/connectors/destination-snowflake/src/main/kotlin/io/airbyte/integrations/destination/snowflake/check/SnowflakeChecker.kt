/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.check

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.SnowflakeSqlNameTransformer
import io.airbyte.integrations.destination.snowflake.client.AirbyteSnowflakeClient
import io.airbyte.integrations.destination.snowflake.client.SnowflakeSqlGenerator
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import jakarta.inject.Singleton
import java.util.UUID
import kotlinx.coroutines.runBlocking

@Singleton
class SnowflakeChecker(
    private val airbyteSnowflakeClient: AirbyteSnowflakeClient,
    private val snowflakeSqlNameTransformer: SnowflakeSqlNameTransformer,
    private val snowflakeSqlGenerator: SnowflakeSqlGenerator,
) : DestinationChecker<SnowflakeConfiguration> {

    override fun check(config: SnowflakeConfiguration) {
        val columnName = "testKey"
        val data = "{\"$columnName\": \"testValue\"}"
        val outputSchema = snowflakeSqlNameTransformer.transform(config.schema)
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
        runBlocking {
            try {
                airbyteSnowflakeClient.createNamespace(outputSchema)
                airbyteSnowflakeClient.createTable(
                    stream = destinationStream,
                    tableName = qualifiedTableName,
                    columnNameMapping = ColumnNameMapping(emptyMap()),
                    replace = true,
                )

                // TODO Insert data here

                // TODO verify record inserted
            } finally {
                airbyteSnowflakeClient.dropTable(qualifiedTableName)
            }
        }
    }
}
