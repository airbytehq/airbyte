/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.check

import io.airbyte.cdk.command.AIRBYTE_CLOUD_ENV
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
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.write.load.PostgresInsertBuffer
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.time.OffsetDateTime
import java.util.UUID
import kotlinx.coroutines.runBlocking

internal const val CHECK_COLUMN_NAME = "test_key"

@Singleton
@Requires(notEnv = [AIRBYTE_CLOUD_ENV])
class PostgresOssChecker(
    private val postgresAirbyteClient: PostgresAirbyteClient,
    private val postgresConfiguration: PostgresConfiguration,
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
                CHECK_COLUMN_NAME to AirbyteValue.from("test-value")
            )
        val outputSchema = postgresConfiguration.schema
        val tableName =
            "_airbyte_connection_test_${
                UUID.randomUUID().toString().replace("-".toRegex(), "")}"
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
                postgresAirbyteClient.createNamespace(outputSchema)
                postgresAirbyteClient.createTable(
                    stream = destinationStream,
                    tableName = qualifiedTableName,
                    columnNameMapping = ColumnNameMapping(emptyMap()),
                    replace = true,
                )

                val columns = postgresAirbyteClient.describeTable(qualifiedTableName)
                val postgresInsertBuffer =
                    PostgresInsertBuffer(
                        tableName = qualifiedTableName,
                        columns = columns,
                        postgresClient = postgresAirbyteClient,
                        postgresConfiguration = postgresConfiguration,
                    )

                postgresInsertBuffer.accumulate(data)
                postgresInsertBuffer.flush()
                val tableCount = postgresAirbyteClient.countTable(qualifiedTableName)
                require(tableCount == 1L) {
                    "Failed to insert expected rows into check table. Actual written: $tableCount"
                }
            } finally {
                postgresAirbyteClient.dropTable(qualifiedTableName)
            }
        }
    }
}
