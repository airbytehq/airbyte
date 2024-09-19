/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.operation

import com.databricks.sdk.WorkspaceClient
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.integrations.base.destination.operation.StorageOperation
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil as tdutils
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksDestinationHandler
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.util.Optional
import java.util.UUID

class DatabricksStorageOperation(
    private val sqlGenerator: DatabricksSqlGenerator,
    private val destinationHandler: DatabricksDestinationHandler,
    private val workspaceClient: WorkspaceClient,
    private val database: String,
    private val purgeStagedFiles: Boolean = false
) : StorageOperation<SerializableBuffer> {

    private val log = KotlinLogging.logger {}

    override fun writeToStage(
        streamConfig: StreamConfig,
        suffix: String,
        data: SerializableBuffer
    ) {
        val streamId = streamConfig.id
        val stagedFile = "${stagingDirectory(streamId, database)}/${data.filename}"
        workspaceClient.files().upload(stagedFile, data.inputStream)
        destinationHandler.execute(
            Sql.of(
                // schema inference sees _airbyte_generation_id as an int (int32),
                // which can't be loaded into a bigint (int64) column.
                // So we have to explicitly cast it to a bigint.
                """
                COPY INTO `$database`.`${streamId.rawNamespace}`.`${streamId.rawName}$suffix`
                FROM (
                  SELECT _airbyte_generation_id :: bigint, * except (_airbyte_generation_id)
                  FROM '$stagedFile'
                )
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

    private fun prepareStagingTable(streamId: StreamId, suffix: String, replace: Boolean) {
        // TODO: Optimize by running SHOW TABLES
        destinationHandler.execute(sqlGenerator.createRawTable(streamId, suffix, replace))
    }

    private fun prepareStagingVolume(streamId: StreamId) {
        destinationHandler.execute(
            Sql.of(
                "CREATE VOLUME IF NOT EXISTS `$database`.`${streamId.rawNamespace}`.`${volumeName(streamId)}`"
            )
        )
        workspaceClient.files().createDirectory(stagingDirectory(streamId, database))
    }

    override fun prepareStage(streamId: StreamId, suffix: String, replace: Boolean) {
        prepareStagingTable(streamId, suffix, replace)
        prepareStagingVolume(streamId)
    }

    override fun overwriteStage(streamId: StreamId, suffix: String) {
        // databricks recommends CREATE OR REPLACE ... AS SELECT
        // instead of dropping the table and then doing more operations
        // https://docs.databricks.com/en/delta/drop-table.html#when-to-replace-a-table
        destinationHandler.execute(
            // Databricks doesn't support transactions, so we have to do these separately
            Sql.separately(
                """
                CREATE OR REPLACE TABLE `$database`.`${streamId.rawNamespace}`.`${streamId.rawName}`
                AS SELECT * FROM `$database`.`${streamId.rawNamespace}`.`${streamId.rawName}$suffix`
                """.trimIndent(),
                "DROP TABLE `$database`.`${streamId.rawNamespace}`.`${streamId.rawName}$suffix`",
            )
        )
    }

    override fun transferFromTempStage(streamId: StreamId, suffix: String) {
        destinationHandler.execute(
            // Databricks doesn't support transactions, so we have to do these separately
            Sql.separately(
                """
                INSERT INTO `$database`.`${streamId.rawNamespace}`.`${streamId.rawName}`
                SELECT * FROM `$database`.`${streamId.rawNamespace}`.`${streamId.rawName}$suffix`
                """.trimIndent(),
                "DROP TABLE `$database`.`${streamId.rawNamespace}`.`${streamId.rawName}$suffix`",
            )
        )
    }

    override fun getStageGeneration(streamId: StreamId, suffix: String): Long? {
        val generationIds =
            destinationHandler.query(
                "SELECT $COLUMN_NAME_AB_GENERATION_ID FROM `$database`.`${streamId.rawNamespace}`.`${streamId.rawName}$suffix` LIMIT 1"
            )
        return if (generationIds.isEmpty()) {
            null
        } else {
            generationIds.first()[COLUMN_NAME_AB_GENERATION_ID].asLong()
        }
    }

    override fun cleanupStage(streamId: StreamId) {
        if (purgeStagedFiles) {
            // This operation might fail if there are files left over for any reason from COPY step
            log.info { "Deleting Staging directory ${stagingDirectory(streamId, database)}" }
            workspaceClient.files().deleteDirectory(stagingDirectory(streamId, database))
        }
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
