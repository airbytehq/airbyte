/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.staging

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction
import io.airbyte.cdk.integrations.destination.jdbc.WriteConfig
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*

private val log = KotlinLogging.logger {}
/** Functions and logic common to all flushing strategies. */
object GeneralStagingFunctions {
    // using a random string here as a placeholder for the moment.
    // This would avoid mixing data in the staging area between different syncs (especially if they
    // manipulate streams with similar names)
    // if we replaced the random connection id by the actual connection_id, we'd gain the
    // opportunity to
    // leverage data that was uploaded to stage
    // in a previous attempt but failed to load to the warehouse for some reason (interrupted?)
    // instead.
    // This would also allow other programs/scripts
    // to load (or reload backups?) in the connection's staging area to be loaded at the next sync.
    val RANDOM_CONNECTION_ID: UUID = UUID.randomUUID()

    fun onStartFunction(
        database: JdbcDatabase,
        stagingOperations: StagingOperations,
        writeConfigs: List<WriteConfig>,
        typerDeduper: TyperDeduper
    ): OnStartFunction {
        return OnStartFunction {
            log.info(
                "Preparing raw tables in destination started for {} streams",
                writeConfigs.size
            )
            typerDeduper.prepareSchemasAndRunMigrations()

            // Create raw tables
            val queryList: MutableList<String> = ArrayList()
            for (writeConfig in writeConfigs) {
                val schema = writeConfig.outputSchemaName
                val stream = writeConfig.streamName
                val dstTableName = writeConfig.outputTableName
                val stageName = stagingOperations.getStageName(schema, dstTableName)
                val stagingPath =
                    stagingOperations.getStagingPath(
                        SerialStagingConsumerFactory.Companion.RANDOM_CONNECTION_ID,
                        schema,
                        stream,
                        writeConfig.outputTableName,
                        writeConfig.writeDatetime
                    )

                log.info(
                    "Preparing staging area in destination started for schema {} stream {}: target table: {}, stage: {}",
                    schema,
                    stream,
                    dstTableName,
                    stagingPath
                )

                stagingOperations.createSchemaIfNotExists(database, schema)
                stagingOperations.createTableIfNotExists(database, schema, dstTableName)
                stagingOperations.createStageIfNotExists(database, stageName)

                when (writeConfig.syncMode) {
                    DestinationSyncMode.OVERWRITE ->
                        queryList.add(
                            stagingOperations.truncateTableQuery(database, schema, dstTableName)
                        )
                    DestinationSyncMode.APPEND,
                    DestinationSyncMode.APPEND_DEDUP -> {}
                    else ->
                        throw IllegalStateException(
                            "Unrecognized sync mode: " + writeConfig.syncMode
                        )
                }
                log.info(
                    "Preparing staging area in destination completed for schema {} stream {}",
                    schema,
                    stream
                )
            }

            typerDeduper.prepareFinalTables()

            log.info("Executing finalization of tables.")
            stagingOperations.executeTransaction(database, queryList)
        }
    }

    /**
     * Handles copying data from staging area to destination table and clean up of staged files if
     * upload was unsuccessful
     */
    @Throws(Exception::class)
    fun copyIntoTableFromStage(
        database: JdbcDatabase?,
        stageName: String?,
        stagingPath: String?,
        stagedFiles: List<String?>?,
        tableName: String?,
        schemaName: String?,
        stagingOperations: StagingOperations,
        streamNamespace: String?,
        streamName: String?,
        typerDeduperValve: TypeAndDedupeOperationValve,
        typerDeduper: TyperDeduper
    ) {
        try {
            val rawTableInsertLock =
                typerDeduper.getRawTableInsertLock(streamNamespace!!, streamName!!)
            rawTableInsertLock.lock()
            try {
                stagingOperations.copyIntoTableFromStage(
                    database,
                    stageName,
                    stagingPath,
                    stagedFiles,
                    tableName,
                    schemaName
                )
            } finally {
                rawTableInsertLock.unlock()
            }

            val streamId = AirbyteStreamNameNamespacePair(streamName, streamNamespace)
            typerDeduperValve.addStreamIfAbsent(streamId)
            if (typerDeduperValve.readyToTypeAndDedupe(streamId)) {
                typerDeduper.typeAndDedupe(streamId.namespace, streamId.name, false)
                typerDeduperValve.updateTimeAndIncreaseInterval(streamId)
            }
        } catch (e: Exception) {
            throw RuntimeException("Failed to upload data from stage $stagingPath", e)
        }
    }

    /**
     * Tear down process, will attempt to try to clean out any staging area
     *
     * @param database database used for syncing
     * @param stagingOperations collection of SQL queries necessary for writing data into a staging
     * area
     * @param writeConfigs configuration settings for all destination connectors needed to write
     * @param purgeStagingData drop staging area if true, keep otherwise
     * @return
     */
    fun onCloseFunction(
        database: JdbcDatabase?,
        stagingOperations: StagingOperations,
        writeConfigs: List<WriteConfig>,
        purgeStagingData: Boolean,
        typerDeduper: TyperDeduper
    ): OnCloseFunction {
        return OnCloseFunction {
            hasFailed: Boolean,
            streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary> ->
            // After moving data from staging area to the target table (airybte_raw) clean up the
            // staging
            // area (if user configured)
            log.info("Cleaning up destination started for {} streams", writeConfigs.size)
            typerDeduper.typeAndDedupe(streamSyncSummaries)
            for (writeConfig in writeConfigs) {
                val schemaName = writeConfig.outputSchemaName
                if (purgeStagingData) {
                    val stageName =
                        stagingOperations.getStageName(schemaName, writeConfig.outputTableName)
                    val stagePath =
                        stagingOperations.getStagingPath(
                            RANDOM_CONNECTION_ID,
                            schemaName,
                            writeConfig.streamName,
                            writeConfig.outputTableName,
                            writeConfig.writeDatetime
                        )
                    log.info(
                        "Cleaning stage in destination started for stream {}. schema {}, stage: {}",
                        writeConfig.streamName,
                        schemaName,
                        stagePath
                    )
                    // TODO: This is another weird manifestation of Redshift vs Snowflake using
                    // either or variables from
                    // stageName/StagingPath.
                    stagingOperations.dropStageIfExists(database, stageName, stagePath)
                }
            }
            typerDeduper.commitFinalTables()
            typerDeduper.cleanup()
            log.info("Cleaning up destination completed.")
        }
    }
}
