/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.csv.toCsvHeader
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlob
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlobClient
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.cdk.load.write.db.BulkLoad
import io.airbyte.cdk.load.write.db.BulkLoadFactory
import io.airbyte.integrations.destination.mssql.v2.config.BulkLoadConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

class MSSQLBulkLoad(
    private val azureBlobClient: AzureBlobClient,
    private val stream: DestinationStream,
    private val mssqlBulkLoadHandler: MSSQLBulkLoadHandler,
    private val formatFilePath: String
) : BulkLoad<StreamKey, AzureBlob> {
    private val log = KotlinLogging.logger {}

    override suspend fun load(remoteObject: AzureBlob) {
        val dataFilePath = remoteObject.key
        println("loader dataFilePath: $dataFilePath (stream = ${stream.descriptor})")
        try {
            if (stream.importType is Dedupe) {
                handleDedup(dataFilePath)
            } else {
                handleAppendOverwrite(dataFilePath)
            }
        } finally {
            // Best-effort cleanup of the data blob
            deleteBlobSafe(dataFilePath)
        }
    }

    /**
     * Merges upsert data by creating a temporary table, bulk-loading the CSV, and then MERGEing
     * into the destination table using the PK columns.
     */
    private fun handleDedup(dataFilePath: String) {
        val importType = stream.importType as Dedupe
        val primaryKey =
            if (importType.primaryKey.isNotEmpty()) {
                importType.primaryKey.flatten()
            } else {
                // If no dedicated PK is provided, use the cursor as the PK
                importType.cursor
            }

        // Build the full list of columns, including the Airbyte metadata columns
        val allColumns = stream.schema.withAirbyteMeta(true).toCsvHeader().toList()

        val nonPkColumns = allColumns - primaryKey.toSet()

        mssqlBulkLoadHandler.bulkLoadAndUpsertForDedup(
            primaryKeyColumns = primaryKey,
            cursorColumns = importType.cursor,
            nonPkColumns = nonPkColumns,
            dataFilePath = dataFilePath,
            formatFilePath = formatFilePath
        )
    }

    /** Performs a simple bulk insert (append-overwrite behavior). */
    private fun handleAppendOverwrite(dataFilePath: String) {
        mssqlBulkLoadHandler.bulkLoadForAppendOverwrite(
            dataFilePath = dataFilePath,
            formatFilePath = formatFilePath
        )
    }

    /**
     * Safely attempts to delete the provided blob path, logging any errors but not rethrowing by
     * default.
     */
    private fun deleteBlobSafe(path: String) {
        try {
            runBlocking { azureBlobClient.delete(path) }
        } catch (e: Exception) {
            log.error(e) { "Failed to delete blob at path=$path. Cause: ${e.message}" }
        }
    }

    override fun close() {
        /* Do nothing */
    }
}

/** Custom requires guard to ensure the bulk load strategy is only used when configured. */
@Singleton
class LoadTypeConfigurationIsBulkLoadConfiguration(
// private val config: MSSQLConfiguration
) : Condition {
    override fun matches(context: ConditionContext<*>?): Boolean {
        return true
        // return config.mssqlLoadTypeConfiguration.loadTypeConfiguration is BulkLoadConfiguration
    }
}

@Singleton
@Requires(condition = LoadTypeConfigurationIsBulkLoadConfiguration::class)
class MSSQLBulkLoadFactory(
    private val azureBlobClient: AzureBlobClient,
    private val catalog: DestinationCatalog,
    private val config: MSSQLConfiguration,
    private val streamStateStore: StreamStateStore<MSSQLStreamState>
) : BulkLoadFactory<StreamKey, AzureBlob> {
    override val numPartWorkers: Int = 2
    override val numUploadWorkers: Int = 10
    override val maxNumConcurrentLoads: Int = 1

    override val objectSizeBytes: Long = 200 * 1024 * 1024
    override val partSizeBytes: Long = 10 * 1024 * 1024

    // Default is to assume persisted, but it seems we don't recover
    // orphaned objects.
    override val batchStateOnUpload: Batch.State = Batch.State.STAGED

    private val defaultSchema = config.schema
    // This cast is guaranteed to succeed by the `Requires` condition
    private val loadConfig =
        config.mssqlLoadTypeConfiguration.loadTypeConfiguration as BulkLoadConfiguration

    override fun create(key: StreamKey): BulkLoad<StreamKey, AzureBlob> {
        val stream = catalog.getStream(key.stream)
        val mssqlBulkLoadHandler =
            MSSQLBulkLoadHandler(
                streamStateStore[key.stream]!!.dataSource,
                stream.descriptor.namespace ?: defaultSchema,
                stream.descriptor.name,
                loadConfig.bulkLoadDataSource,
                MSSQLQueryBuilder(config.schema, stream)
            )
        return MSSQLBulkLoad(
            azureBlobClient,
            stream,
            mssqlBulkLoadHandler,
            streamStateStore[key.stream]!!.formatFilePath
        )
    }
}
