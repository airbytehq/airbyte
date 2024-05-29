/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.staging

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import java.time.Instant
import java.util.*

/**
 * Staging operations focuses on the SQL queries that are needed to success move data into a staging
 * environment like GCS or S3. In general, the reference of staging is the usage of an object
 * storage for the purposes of efficiently uploading bulk data to destinations
 *
 * TODO: This interface is shared between Snowflake and Redshift connectors where the staging
 * mechanism is different wire protocol. Make the interface more Generic and have sub interfaces to
 * support BlobStorageOperations or Jdbc based staging operations.
 */
interface StagingOperations : SqlOperations {
    /**
     * @param outputTableName The name of the table this staging file will be loaded into (typically
     * a raw table). Not all destinations use the table name in the staging path (e.g. Snowflake
     * simply uses a timestamp + UUID), but e.g. Redshift does rely on this to ensure uniqueness.
     */
    fun getStagingPath(
        connectionId: UUID?,
        namespace: String?,
        streamName: String?,
        outputTableName: String?,
        writeDatetime: Instant?
    ): String?

    /**
     * Returns the staging environment's name
     *
     * @param namespace Name of schema
     * @param streamName Name of the stream
     * @return Fully qualified name of the staging environment
     */
    fun getStageName(namespace: String?, streamName: String?): String?

    /**
     * Create a staging folder where to upload temporary files before loading into the final
     * destination
     */
    @Throws(Exception::class)
    fun createStageIfNotExists(database: JdbcDatabase?, stageName: String?)

    /**
     * Upload the data file into the stage area.
     *
     * @param database database used for syncing
     * @param recordsData records stored in in-memory buffer
     * @param schemaName name of schema
     * @param stagingPath path of staging folder to data files
     * @return the name of the file that was uploaded.
     */
    @Throws(Exception::class)
    fun uploadRecordsToStage(
        database: JdbcDatabase?,
        recordsData: SerializableBuffer?,
        schemaName: String?,
        stageName: String?,
        stagingPath: String?
    ): String

    /**
     * Load the data stored in the stage area into a temporary table in the destination
     *
     * @param database database interface
     * @param stagingPath path to staging files
     * @param stagedFiles collection of staged files
     * @param tableName name of table to write staging files to
     * @param schemaName name of schema
     */
    @Throws(Exception::class)
    fun copyIntoTableFromStage(
        database: JdbcDatabase?,
        stageName: String?,
        stagingPath: String?,
        stagedFiles: List<String>?,
        tableName: String?,
        schemaName: String?
    )

    /**
     * Delete the stage area and all staged files that was in it
     *
     * @param database database used for syncing
     * @param stageName Name of the staging area used to store files
     */
    @Throws(Exception::class)
    fun dropStageIfExists(database: JdbcDatabase?, stageName: String?, stagingPath: String?)
}
