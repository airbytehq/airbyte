/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.jdbc

import com.databricks.sdk.WorkspaceClient
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeTransaction
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.util.*

class DatabricksStorageOperations(
    private val sqlGenerator: SqlGenerator,
    private val destinationHandler: DestinationHandler<MinimumDestinationState.Impl>,
    private val workspaceClient: WorkspaceClient,
    private val database: String,
    private val purgeStagedFiles: Boolean = false
) {

    private val log = KotlinLogging.logger {}

    // TODO: There are 2 methods used from SqlGenerator which were spread across in old code.
    //  Hoist them to SqlGenerator interface in CDK, until then using concrete instance.
    private val databricksSqlGenerator = sqlGenerator as DatabricksSqlGenerator

    fun copyIntoStagingTable(streamConfig: StreamConfig, buffer: SerializableBuffer) {
        val stagedFile = "${stagingDirectory(streamConfig.id, database)}/${buffer.filename}"
        workspaceClient.files().upload(stagedFile, buffer.inputStream)
        destinationHandler.execute(
            Sql.of(
                """
                        COPY INTO $database.${streamConfig.id.rawNamespace}.${streamConfig.id.rawName}
                        FROM '$stagedFile'
                        FILEFORMAT = CSV
                        FORMAT_OPTIONS ('header'='true', 'inferSchema'='true', 'escape'='"');
                    """.trimIndent(),
            ),
        )
        // Databricks recommends that partners delete files in the staging directory once the data
        // is
        // ingested into Delta Lake. Partners can use the SQL REMOVE API to delete files from the
        // staging
        // location. You can find detailed information about APIs in the Appendix.
        // The delete operation has to be done on a file level. You can NOT delete a folder and its
        // contents
        // recursively.
        if (purgeStagedFiles) {
            Sql.of("REMOVE ${stagingDirectory(streamConfig.id, database)}/${buffer.filename}")
        }
    }

    fun typeAndDedupe(
        streamConfig: StreamConfig,
        maxProcessedTimestamp: Optional<Instant>,
        finalTableSuffix: String
    ) {
        TypeAndDedupeTransaction.executeTypeAndDedupe(
            sqlGenerator,
            destinationHandler,
            streamConfig,
            maxProcessedTimestamp,
            finalTableSuffix,
        )
    }

    fun overwriteFinalTable(streamConfig: StreamConfig, suffix: String) {
        log.info {
            "Overwriting table ${streamConfig.id.finalTableId(DatabricksSqlGenerator.QUOTE)} with ${
                streamConfig.id.finalTableId(
                    DatabricksSqlGenerator.QUOTE,
                    suffix,
                )
            }"
        }
        destinationHandler.execute(sqlGenerator.overwriteFinalTable(streamConfig.id, suffix))
    }

    fun prepareStagingTable(streamId: StreamId, destinationSyncMode: DestinationSyncMode) {
        val rawSchema = streamId.rawNamespace
        // TODO: Optimize by running SHOW SCHEMAS; rather than CREATE SCHEMA if not exists
        destinationHandler.execute(sqlGenerator.createSchema(rawSchema))

        // TODO: Optimize by running SHOW TABLES; truncate or create based on mode
        // Create raw tables.
        destinationHandler.execute(databricksSqlGenerator.createRawTable(streamId))
        // Truncate the raw table if sync in OVERWRITE.
        if (destinationSyncMode == DestinationSyncMode.OVERWRITE) {
            destinationHandler.execute(databricksSqlGenerator.truncateRawTable(streamId))
        }
    }

    fun createSchemaIfNotExists(streamConfig: StreamConfig) {
        val finalSchema = streamConfig.id.finalNamespace
        // TODO: Optimize by running SHOW SCHEMAS; rather than CREATE SCHEMA if not exists
        destinationHandler.execute(sqlGenerator.createSchema(finalSchema))
    }

    fun createFinalTable(streamConfig: StreamConfig, suffix: String, replace: Boolean) {
        // The table doesn't exist. Create it. Don't force.
        destinationHandler.execute(
            sqlGenerator.createTable(streamConfig, suffix, replace),
        )
    }

    fun executeSoftReset(streamConfig: StreamConfig) {
        TypeAndDedupeTransaction.executeSoftReset(
            sqlGenerator,
            destinationHandler,
            streamConfig,
        )
    }

    fun prepareStagingVolume(streamId: StreamId) {
        destinationHandler.execute(
            Sql.of("CREATE VOLUME $database.`${streamId.rawNamespace}`.${volumeName(streamId)}")
        )
        workspaceClient.files().createDirectory(stagingDirectory(streamId, database))
    }

    companion object {
        private const val VOLUMES_BASE_PATH = "/Volumes"

        // When connectionId can be passed into connector, use that. For now just a UUID stamped at
        // start of execution
        private val connectionId = UUID.randomUUID()
        private val executionInstant = Instant.now()

        // Deterministic path constructed using streamId
        fun stagingDirectory(streamId: StreamId, database: String): String {
            val zdt: ZonedDateTime = executionInstant.atZone(ZoneOffset.UTC)
            return "$VOLUMES_BASE_PATH/$database/${streamId.rawNamespace}/${volumeName(streamId)}/" +
                "${zdt.year}_${zdt.monthValue}_${zdt.dayOfMonth}_${zdt.hour}_$connectionId"
        }

        fun volumeName(streamId: StreamId): String {
            return "${streamId.rawName}_staging"
        }
    }
}
