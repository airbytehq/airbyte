/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.check

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
import io.airbyte.integrations.destination.mysql_v2.client.MysqlAirbyteClient
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlConfiguration
import io.airbyte.integrations.destination.mysql_v2.sql.MysqlColumnUtils
import io.airbyte.integrations.destination.mysql_v2.write.load.MysqlInsertBuffer
import jakarta.inject.Singleton
import java.time.OffsetDateTime
import java.util.UUID
import kotlinx.coroutines.runBlocking

internal const val CHECK_COLUMN_NAME = "test_key"

/**
 * Verifies that the MySQL destination is properly configured and accessible.
 *
 * This checker:
 * 1. Creates a temporary test table
 * 2. Inserts a test record
 * 3. Verifies the record count
 * 4. Cleans up the test table
 *
 * If any step fails, the check operation will report an error to the user.
 */
@Singleton
class MysqlChecker(
    private val mysqlAirbyteClient: MysqlAirbyteClient,
    private val mysqlConfiguration: MysqlConfiguration,
    private val mysqlColumnUtils: MysqlColumnUtils,
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

        val outputSchema = mysqlConfiguration.database
        val tableName =
            "_airbyte_connection_test_${UUID.randomUUID().toString().replace("-".toRegex(), "")}"
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
                // Create the test table
                mysqlAirbyteClient.createTable(
                    stream = destinationStream,
                    tableName = qualifiedTableName,
                    columnNameMapping = ColumnNameMapping(emptyMap()),
                    replace = true,
                )

                // Get the columns for the insert buffer
                val columns = mysqlAirbyteClient.describeTable(qualifiedTableName)

                // Create an insert buffer and write test data
                val mysqlInsertBuffer =
                    MysqlInsertBuffer(
                        tableName = qualifiedTableName,
                        columns = columns.keys.toList(),
                        mysqlClient = mysqlAirbyteClient,
                        flushLimit = mysqlConfiguration.batchSize,
                    )

                mysqlInsertBuffer.accumulate(data)
                mysqlInsertBuffer.flush()

                // Verify the record was inserted
                val tableCount = mysqlAirbyteClient.countTable(qualifiedTableName)
                require(tableCount == 1L) {
                    "Failed to insert expected rows into check table. Actual written: $tableCount"
                }
            } finally {
                // Always clean up the test table
                mysqlAirbyteClient.dropTable(qualifiedTableName)
            }
        }
    }
}
