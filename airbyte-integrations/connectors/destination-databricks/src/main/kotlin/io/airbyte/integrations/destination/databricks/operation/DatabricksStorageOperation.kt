/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.operation

import com.databricks.sdk.WorkspaceClient
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.integrations.base.destination.operation.StorageOperation
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil as tdutils
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksSqlGenerator
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.util.*

class DatabricksStorageOperation(
    private val sqlGenerator: SqlGenerator,
    private val destinationHandler: DestinationHandler<MinimumDestinationState.Impl>,
    private val workspaceClient: WorkspaceClient,
    private val database: String,
    private val purgeStagedFiles: Boolean = false
) : StorageOperation<SerializableBuffer> {

    private val log = KotlinLogging.logger {}

    // TODO: There are 2 methods used from SqlGenerator which were spread across in old code.
    //  Hoist them to SqlGenerator interface in CDK, until then using concrete instance.
    private val databricksSqlGenerator = sqlGenerator as DatabricksSqlGenerator

    override fun writeToStage(streamId: StreamId, data: SerializableBuffer) {
        val stagedFile = "${stagingDirectory(streamId, database)}/${data.filename}"
        workspaceClient.files().upload(stagedFile, data.inputStream)
        destinationHandler.execute(
            Sql.of(
                """
                        COPY INTO `$database`.`${streamId.rawNamespace}`.`${streamId.rawName}`
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
            log.info {
                "Removing staged file ${stagingDirectory(streamId, database)}/${data.filename}"
            }
            // Using Jdbc for PUT 'file' and REMOVE 'file' just returns a presigned S3 url and the
            // HTTP method to call as
            // in sql row data. Using workspace client instead.
            // destinationHandler.execute(Sql.of("REMOVE '${stagingDirectory(streamConfig.id,
            // database)}/${buffer.filename}'"))
            workspaceClient
                .files()
                .delete("${stagingDirectory(streamId, database)}/${data.filename}")
        }
    }

    override fun typeAndDedupe(
        streamConfig: StreamConfig,
        maxProcessedTimestamp: Optional<Instant>,
        finalTableSuffix: String
    ) {
        tdutils.executeTypeAndDedupe(
            sqlGenerator,
            destinationHandler,
            streamConfig,
            maxProcessedTimestamp,
            finalTableSuffix,
        )
    }

    private fun prepareStagingTable(streamId: StreamId, destinationSyncMode: DestinationSyncMode) {
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

    private fun prepareStagingVolume(streamId: StreamId) {
        destinationHandler.execute(
            Sql.of(
                "CREATE VOLUME IF NOT EXISTS `$database`.`${streamId.rawNamespace}`.`${volumeName(streamId)}`"
            )
        )
        workspaceClient.files().createDirectory(stagingDirectory(streamId, database))
    }

    override fun prepareStage(streamId: StreamId, destinationSyncMode: DestinationSyncMode) {
        prepareStagingTable(streamId, destinationSyncMode)
        prepareStagingVolume(streamId)
    }

    override fun cleanupStage(streamId: StreamId) {
        if (purgeStagedFiles) {
            // This operation might fail if there are files left over for any reason from COPY step
            log.info { "Deleting Staging directory ${stagingDirectory(streamId, database)}" }
            workspaceClient.files().deleteDirectory(stagingDirectory(streamId, database))
        }
    }

    override fun createFinalNamespace(streamId: StreamId) {
        val finalSchema = streamId.finalNamespace
        // TODO: Optimize by running SHOW SCHEMAS; rather than CREATE SCHEMA if not exists
        destinationHandler.execute(sqlGenerator.createSchema(finalSchema))
    }

    override fun createFinalTable(streamConfig: StreamConfig, suffix: String, replace: Boolean) {
        // The table doesn't exist. Create it. Don't force.
        destinationHandler.execute(
            sqlGenerator.createTable(streamConfig, suffix, replace),
        )
    }

    override fun softResetFinalTable(streamConfig: StreamConfig) {
        tdutils.executeSoftReset(
            sqlGenerator,
            destinationHandler,
            streamConfig,
        )
    }

    override fun overwriteFinalTable(streamConfig: StreamConfig, tmpTableSuffix: String) {
        // Guard to not accidentally overwrite existing table or DROP it.
        if (tmpTableSuffix.isNotBlank()) {
            log.info {
                "Overwriting table ${streamConfig.id.finalTableId(DatabricksSqlGenerator.QUOTE)} with ${
                    streamConfig.id.finalTableId(
                        DatabricksSqlGenerator.QUOTE,
                        tmpTableSuffix,
                    )
                }"
            }
            destinationHandler.execute(
                sqlGenerator.overwriteFinalTable(streamConfig.id, tmpTableSuffix)
            )
        }
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
