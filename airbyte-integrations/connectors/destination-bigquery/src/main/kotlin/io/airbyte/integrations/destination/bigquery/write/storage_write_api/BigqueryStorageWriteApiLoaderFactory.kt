/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.write.storage_write_api

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.storage.v1.BigQueryWriteClient
import com.google.cloud.bigquery.storage.v1.JsonStreamWriter
import com.google.cloud.bigquery.storage.v1.TableName
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogByDescriptor
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingExecutionConfig
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.StorageWriteApiConfiguration
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.toTableId
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

/**
 * Condition class to enable Storage Write API loader only when configured.
 */
class BigqueryConfiguredForStorageWriteApi : Condition {
    override fun matches(context: ConditionContext<*>): Boolean {
        val config = context.beanContext.getBean(BigqueryConfiguration::class.java)
        return config.loadingMethod is StorageWriteApiConfiguration
    }
}

/**
 * Factory for creating BigqueryStorageWriteApiLoader instances.
 *
 * Manages JsonStreamWriter lifecycle and coordinates with state stores.
 */
@Requires(condition = BigqueryConfiguredForStorageWriteApi::class)
@Singleton
class BigqueryStorageWriteApiLoaderFactory(
    private val catalog: DestinationCatalog,
    private val bigquery: BigQuery,
    private val bigqueryWriteClient: BigQueryWriteClient,
    private val config: BigqueryConfiguration,
    private val tableCatalog: TableCatalogByDescriptor,
    private val typingDedupingStreamStateStore: StreamStateStore<TypingDedupingExecutionConfig>?,
    private val directLoadStreamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>?,
) : DirectLoaderFactory<BigqueryStorageWriteApiLoader> {

    private val storageApiConfig = config.loadingMethod as StorageWriteApiConfiguration

    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int,
    ): BigqueryStorageWriteApiLoader {
        val tableNameInfo = tableCatalog[streamDescriptor]
            ?: throw IllegalStateException("Table name info not found for stream $streamDescriptor")

        // Determine table ID and schema based on mode
        val tableName: TableName
        val legacyRawTablesOnly: Boolean

        if (config.legacyRawTablesOnly) {
            legacyRawTablesOnly = true
            val rawTableName = tableNameInfo.tableNames.rawTableName
                ?: throw IllegalStateException("Raw table name not found for stream $streamDescriptor")

            // Wait for state store to be populated
            val rawTableSuffix =
                waitForStateStore(typingDedupingStreamStateStore!!, streamDescriptor).rawTableSuffix

            val tableId = com.google.cloud.bigquery.TableId.of(
                rawTableName.namespace,
                rawTableName.name + rawTableSuffix
            )

            tableName = TableName.of(
                tableId.project ?: config.projectId,
                tableId.dataset,
                tableId.table
            )
        } else {
            legacyRawTablesOnly = false

            // Wait for state store to be populated
            val executionConfig = waitForStateStore(directLoadStreamStateStore!!, streamDescriptor)
            val tableId = executionConfig.tableName.toTableId()

            tableName = TableName.of(
                tableId.project ?: config.projectId,
                tableId.dataset,
                tableId.table
            )
        }

        // Verify table exists
        val bqTableId = com.google.cloud.bigquery.TableId.of(
            tableName.project,
            tableName.dataset,
            tableName.table
        )
        val table = bigquery.getTable(bqTableId)
            ?: throw ConfigErrorException(
                """
                |Table ${tableName.project}.${tableName.dataset}.${tableName.table} does not exist.
                |Please ensure the table is created before attempting to write to it.
                """.trimMargin()
            )

        logger.info {
            "Creating Storage Write API loader for table ${tableName.project}.${tableName.dataset}.${tableName.table}"
        }

        // Create JSON stream writer with default stream
        val streamWriter = try {
            JsonStreamWriter.newBuilder(tableName.toString(), bigqueryWriteClient)
                .build()
        } catch (e: Exception) {
            logger.error(e) {
                "Failed to create JsonStreamWriter for table ${tableName.project}.${tableName.dataset}.${tableName.table}"
            }
            throw ConfigErrorException(
                """
                |Failed to create Storage Write API stream for table ${tableName.project}.${tableName.dataset}.${tableName.table}.
                |Error: ${e.message}
                |Please verify:
                |  1. Service account has BigQuery Data Editor role
                |  2. Table exists and is accessible
                |  3. Dataset location matches the configured location
                """.trimMargin(),
                e
            )
        }

        // Create record formatter
        val recordFormatter = BigqueryStorageWriteRecordFormatter(
            columnNameMapping = tableNameInfo.columnNameMapping,
            legacyRawTablesOnly = legacyRawTablesOnly,
        )

        return BigqueryStorageWriteApiLoader(
            tableName = tableName,
            streamWriter = streamWriter,
            recordFormatter = recordFormatter,
            config = storageApiConfig,
        )
    }

    /**
     * Wait for state store to be populated by the coordinating StreamLoader thread.
     */
    private fun <S> waitForStateStore(
        stateStore: StreamStateStore<S>,
        streamDescriptor: DestinationStream.Descriptor
    ): S {
        var attempts = 0
        val maxAttempts = 60 * 60 // 1 hour (1 second intervals)

        while (attempts < maxAttempts) {
            val state = stateStore.get(streamDescriptor)
            if (state != null) {
                logger.debug { "State store populated for stream $streamDescriptor after $attempts attempts" }
                return state
            }

            Thread.sleep(1000)
            attempts++
        }

        throw RuntimeException(
            """
            |Timeout waiting for StreamStateStore to be populated for stream $streamDescriptor.
            |This indicates a coordination issue between workers.
            |Waited for ${maxAttempts / 60} minutes.
            """.trimMargin()
        )
    }
}
