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
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.schema.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeInsertBuffer
import jakarta.inject.Singleton
import java.time.OffsetDateTime
import java.util.UUID
import kotlinx.coroutines.runBlocking

internal const val CHECK_COLUMN_NAME = "test_key"

@Singleton
class SnowflakeChecker(
    private val snowflakeAirbyteClient: SnowflakeAirbyteClient,
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val snowflakeColumnUtils: SnowflakeColumnUtils,
) : DestinationCheckerV2 {

    override fun check() {
        val data =
            mapOf(
                Meta.AirbyteMetaFields.RAW_ID.fieldName to
                    AirbyteValue.from(UUID.randomUUID().toString()),
                Meta.AirbyteMetaFields.EXTRACTED_AT.fieldName to
                    AirbyteValue.from(OffsetDateTime.now()),
                Meta.AirbyteMetaFields.META.fieldName to
                    AirbyteValue.from(emptyMap<String, String>()),
                Meta.AirbyteMetaFields.GENERATION_ID.fieldName to AirbyteValue.from(0),
                CHECK_COLUMN_NAME.toSnowflakeCompatibleName() to AirbyteValue.from("test-value")
            )
        val outputSchema = snowflakeConfiguration.schema.toSnowflakeCompatibleName()
        val tableName =
            "_airbyte_connection_test_${
                UUID.randomUUID().toString().replace("-".toRegex(), "")}".toSnowflakeCompatibleName()
        val qualifiedTableName = TableName(namespace = outputSchema, name = tableName)
        val destinationStream =
            DestinationStream(
                unmappedNamespace = outputSchema,
                unmappedName = tableName,
                importType = Append,
                schema =
                    ObjectType(
                        linkedMapOf(CHECK_COLUMN_NAME to FieldType(StringType, nullable = false))
                    ),
                generationId = 0L,
                minimumGenerationId = 0L,
                syncId = 0L,
                namespaceMapper = NamespaceMapper()
            )
        runBlocking {
            try {
                snowflakeAirbyteClient.createNamespace(outputSchema)
                snowflakeAirbyteClient.createTable(
                    stream = destinationStream,
                    tableName = qualifiedTableName,
                    columnNameMapping = ColumnNameMapping(emptyMap()),
                    replace = true,
                )

                val columns = snowflakeAirbyteClient.describeTable(qualifiedTableName)
                val snowflakeInsertBuffer =
                    SnowflakeInsertBuffer(
                        tableName = qualifiedTableName,
                        columns = columns,
                        snowflakeClient = snowflakeAirbyteClient,
                        snowflakeConfiguration = snowflakeConfiguration,
                        snowflakeColumnUtils = snowflakeColumnUtils,
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
