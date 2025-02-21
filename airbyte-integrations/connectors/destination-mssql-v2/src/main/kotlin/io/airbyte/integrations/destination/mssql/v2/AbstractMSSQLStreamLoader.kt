/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import javax.sql.DataSource

/**
 * Abstract base class for MSSQL-related stream loaders that share common tasks:
 * - Ensuring the destination table exists
 * - Truncating previous data generations when the stream completes successfully
 */
abstract class AbstractMSSQLStreamLoader(
    protected val dataSource: DataSource,
    override val stream: DestinationStream,
    protected val sqlBuilder: MSSQLQueryBuilder
) : StreamLoader {

    protected val log = KotlinLogging.logger {}

    /** Called before processing begins. By default, ensures that the target table exists. */
    override suspend fun start() {
        ensureTableExists()
        super.start()
    }

    /**
     * Called after processing completes or fails. By default, if there was no failure, attempts to
     * truncate previous data generations.
     */
    override suspend fun close(streamFailure: StreamProcessingFailed?) {
        if (streamFailure == null) {
            truncatePreviousGenerations()
        }
        super.close(streamFailure)
    }

    /** Ensures the table exists, creating it if needed, and updates its schema if necessary. */
    private fun ensureTableExists() {
        try {
            dataSource.connection.use { connection ->
                sqlBuilder.createTableIfNotExists(connection)
                sqlBuilder.updateSchema(connection)
            }
        } catch (ex: Exception) {
            log.error(ex) { "Error creating/updating the table: ${ex.message}" }
            throw ex
        }
    }

    /** Removes data from older "generations," usually after a successful sync. */
    private fun truncatePreviousGenerations() {
        try {
            dataSource.connection.use { connection ->
                sqlBuilder.deletePreviousGenerations(connection, stream.minimumGenerationId)
            }
        } catch (e: Exception) {
            log.error(e) { "Error while truncating previous generations. Cause: ${e.message}" }
            throw e
        }
    }
}
