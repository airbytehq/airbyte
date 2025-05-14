/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlobClient
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamStateStore
import javax.sql.DataSource
import kotlinx.coroutines.runBlocking

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION")
class MSSQLBulkLoadStreamLoader(
    override val stream: DestinationStream,
    dataSource: DataSource,
    sqlBuilder: MSSQLQueryBuilder,
    private val defaultSchema: String,
    private val azureBlobClient: AzureBlobClient,
    private val streamStateStore: StreamStateStore<MSSQLStreamState>,
) : AbstractMSSQLStreamLoader(dataSource, stream, sqlBuilder) {

    // Bulk-load related collaborators
    private val mssqlFormatFileCreator = MSSQLFormatFileCreator(dataSource, stream, azureBlobClient)

    /** Lazily initialized when [start] is called. */
    private lateinit var formatFilePath: String

    /**
     * Override start so we can do the standard table existence check, then create & upload the
     * format file.
     */
    override suspend fun start() {
        super.start() // calls ensureTableExists()
        formatFilePath = mssqlFormatFileCreator.createAndUploadFormatFile(defaultSchema).key
        val state = MSSQLBulkLoaderStreamState(dataSource, formatFilePath)
        streamStateStore.put(stream.descriptor, state)
    }

    /**
     * If the stream finishes successfully, super.close() will handle truncating previous
     * generations. We also delete the format file from Blob.
     */
    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        deleteBlobSafe(formatFilePath)
        super.close(hadNonzeroRecords = hadNonzeroRecords, streamFailure)
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
}

/**
 * For use by the new interface (to pass stream state creating during `start` to the BulkLoad
 * loader.)
 */
sealed interface MSSQLStreamState {
    val dataSource: DataSource
}

data class MSSQLBulkLoaderStreamState(
    override val dataSource: DataSource,
    val formatFilePath: String
) : MSSQLStreamState

data class MSSQLDirectLoaderStreamState(
    override val dataSource: DataSource,
    val sqlBuilder: MSSQLQueryBuilder
) : MSSQLStreamState
