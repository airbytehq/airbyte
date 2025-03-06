/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.MSSQLCSVFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.data.csv.toCsvHeader
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.DefaultTimeProvider
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlobClient
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.object_storage.LoadedObject
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.BatchAccumulator
import io.airbyte.cdk.load.write.object_storage.PartToObjectAccumulator
import io.airbyte.cdk.load.write.object_storage.RecordToPartAccumulator
import java.io.ByteArrayOutputStream
import java.util.concurrent.atomic.AtomicLong
import javax.sql.DataSource
import kotlinx.coroutines.runBlocking

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION")
class MSSQLBulkLoadStreamLoader(
    override val stream: DestinationStream,
    dataSource: DataSource,
    sqlBuilder: MSSQLQueryBuilder,
    bulkUploadDataSource: String,
    private val defaultSchema: String,
    private val azureBlobClient: AzureBlobClient,
    private val validateValuesPreLoad: Boolean,
    private val recordBatchSizeOverride: Long? = null
) : AbstractMSSQLStreamLoader(dataSource, stream, sqlBuilder) {

    // Bulk-load related collaborators
    private val mssqlFormatFileCreator = MSSQLFormatFileCreator(dataSource, stream, azureBlobClient)
    private val objectAccumulator = PartToObjectAccumulator(stream, azureBlobClient)
    private val mssqlBulkLoadHandler =
        MSSQLBulkLoadHandler(
            dataSource,
            stream.descriptor.namespace ?: defaultSchema,
            stream.descriptor.name,
            bulkUploadDataSource,
            sqlBuilder
        )

    /** Lazily initialized when [start] is called. */
    private lateinit var formatFilePath: String

    /**
     * Override start so we can do the standard table existence check, then create & upload the
     * format file.
     */
    override suspend fun start() {
        super.start() // calls ensureTableExists()
        formatFilePath = mssqlFormatFileCreator.createAndUploadFormatFile(defaultSchema).key
    }

    /**
     * If the stream finishes successfully, super.close() will handle truncating previous
     * generations. We also delete the format file from Blob.
     */
    override suspend fun close(streamFailure: StreamProcessingFailed?) {
        deleteBlobSafe(formatFilePath)
        super.close(streamFailure)
    }

    /**
     * Creates the batch accumulator that buffers records and writes them out to temporary CSV files
     * in Azure Blob Storage.
     */
    override suspend fun createBatchAccumulator(): BatchAccumulator {
        val writerFactory =
            BufferedFormattingWriterFactory(
                ObjectStorageFormattingWriterFactory(CsvFormatProvider(validateValuesPreLoad)),
                NoOpCompressionProvider()
            )

        val objectStoragePathFactory =
            ObjectStoragePathFactory(
                pathConfigProvider = PathProvider(),
                timeProvider = DefaultTimeProvider()
            )

        return RecordToPartAccumulator(
            objectStoragePathFactory,
            writerFactory,
            partSizeBytes = ObjectStorageUploadConfiguration.DEFAULT_PART_SIZE_BYTES,
            fileSizeBytes = recordBatchSizeOverride
                    ?: ObjectStorageUploadConfiguration.DEFAULT_FILE_SIZE_BYTES,
            stream = stream,
            fileNumber = AtomicLong(0),
            fileNameMapper = { it }
        )
    }

    /**
     * Processes each completed batch. Once a part is fully uploaded to Azure, this method is
     * called. If the stream uses dedup (with primary keys), we merge upsert the data. Otherwise, we
     * simply perform an append-overwrite bulk insert.
     */
    override suspend fun processBatch(batch: Batch): Batch {
        val processedBatch = objectAccumulator.processBatch(batch)
        if (processedBatch is LoadedObject<*> && !processedBatch.isEmpty) {
            val dataFilePath = processedBatch.groupId

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
        return processedBatch
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

    /** A no-op compression provider for objects in Azure. */
    private class NoOpCompressionProvider :
        ObjectStorageCompressionConfigurationProvider<ByteArrayOutputStream> {
        override val objectStorageCompressionConfiguration =
            ObjectStorageCompressionConfiguration(compressor = NoopProcessor)
    }

    /** Provides a CSV format configuration for object storage. */
    private class CsvFormatProvider(validateValuesPreLoad: Boolean) :
        ObjectStorageFormatConfigurationProvider {
        override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration =
            MSSQLCSVFormatConfiguration(validateValuesPreLoad = validateValuesPreLoad)
    }

    /** Defines how blob paths are constructed. For example, "blob/.../{timestamp}/..." etc. */
    private class PathProvider : ObjectStoragePathConfigurationProvider {
        override val objectStoragePathConfiguration =
            ObjectStoragePathConfiguration(
                prefix = "blob",
                pathPattern = "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}/\${MONTH}/\${DAY}/\${EPOCH}/",
                fileNamePattern = "{part_number}{format_extension}",
            )
    }
}
