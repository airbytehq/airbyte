/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.check

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.databricks.client.DatabricksAirbyteClient
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfiguration
import io.airbyte.integrations.destination.databricks.write.load.DatabricksInsertBuffer
import jakarta.inject.Singleton
import java.time.Instant
import java.time.OffsetDateTime
import java.util.*
import kotlinx.coroutines.runBlocking

/**
 * Validates Databricks connectivity by running a full end-to-end mini-sync: namespace creation,
 * table DDL, Unity Catalog Volume staging (file upload + COPY INTO), and row verification.
 */
@Singleton
class DatabricksChecker(
    private val databricksClient: DatabricksAirbyteClient,
    private val config: DatabricksConfiguration,
) : DestinationChecker {

    private var checkTableName: TableName? = null

    override fun check() {
        require(config.acceptTerms) {
            "You must agree to the Databricks JDBC Driver Terms & Conditions to use this connector. " +
                "Set 'accept_terms' to true in the connector configuration."
        }

        val namespace = config.schema.lowercase()
        val tableName = "_airbyte_check_${Instant.now().epochSecond}"
        val table = TableName(namespace = namespace, name = tableName)
        checkTableName = table

        runBlocking {
            databricksClient.createNamespace(namespace)
            databricksClient.createTable(
                stream = buildCheckStream(namespace, tableName, table),
                tableName = table,
                columnNameMapping = ColumnNameMapping(emptyMap()),
                replace = true,
            )

            val columnSchema = databricksClient.describeTable(table)
            val buffer =
                DatabricksInsertBuffer(
                    tableName = table,
                    columns = columnSchema.keys.toList(),
                    columnSchema = columnSchema,
                    databricksClient = databricksClient,
                    config = config,
                )

            buffer.accumulate(buildCheckRecord())
            buffer.flush()

            val count = databricksClient.countTable(table)
            require(count == 1L) {
                "Check failed: expected 1 row in ${table.namespace}.${table.name}, got $count"
            }
        }
    }

    override fun cleanup() {
        checkTableName?.let { runBlocking { databricksClient.dropTable(it) } }
    }

    companion object {
        /** Builds a minimal [DestinationStream] with meta columns only (no user columns). */
        internal fun buildCheckStream(
            namespace: String,
            tableName: String,
            table: TableName,
        ): DestinationStream =
            DestinationStream(
                unmappedNamespace = namespace,
                unmappedName = tableName,
                generationId = 0L,
                minimumGenerationId = 0L,
                syncId = 0L,
                namespaceMapper = NamespaceMapper(),
                tableSchema =
                    StreamTableSchema(
                        tableNames =
                            TableNames(
                                finalTableName = table,
                                tempTableName = table,
                            ),
                        columnSchema =
                            ColumnSchema(
                                inputSchema = emptyMap(),
                                inputToFinalColumnNames = emptyMap(),
                                finalSchema = emptyMap(),
                            ),
                        importType = Append,
                    ),
            )

        /** Builds a test record with all required Airbyte meta column values. */
        internal fun buildCheckRecord(): Map<String, AirbyteValue> =
            mapOf(
                Meta.COLUMN_NAME_AB_RAW_ID to AirbyteValue.from(UUID.randomUUID().toString()),
                Meta.COLUMN_NAME_AB_EXTRACTED_AT to AirbyteValue.from(OffsetDateTime.now()),
                Meta.COLUMN_NAME_AB_META to AirbyteValue.from("{}"),
                Meta.COLUMN_NAME_AB_GENERATION_ID to AirbyteValue.from(0L),
            )
    }
}
