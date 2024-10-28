/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.staging

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction
import io.airbyte.cdk.integrations.destination.jdbc.WriteConfig
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper
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
            log.info {
                "Preparing raw tables in destination started for ${writeConfigs.size} streams"
            }
            typerDeduper.prepareSchemasAndRunMigrations()

            // Create raw tables
            val queryList: MutableList<String> = ArrayList()
            for (writeConfig in writeConfigs) {
                val schema = writeConfig.rawNamespace
                val stream = writeConfig.streamName
                val dstTableName = writeConfig.rawTableName
                val stageName = stagingOperations.getStageName(schema, dstTableName)
                val stagingPath =
                    stagingOperations.getStagingPath(
                        RANDOM_CONNECTION_ID,
                        schema,
                        stream,
                        writeConfig.rawTableName,
                        writeConfig.writeDatetime
                    )

                log.info {
                    "Preparing staging area in destination started for schema $schema stream $stream: target table: $dstTableName, stage: $stagingPath"
                }

                stagingOperations.createSchemaIfNotExists(database, schema)
                stagingOperations.createTableIfNotExists(database, schema, dstTableName)
                stagingOperations.createStageIfNotExists(database, stageName)

                when (writeConfig.minimumGenerationId) {
                    writeConfig.generationId ->
                        queryList.add(
                            stagingOperations.truncateTableQuery(
                                database,
                                schema,
                                dstTableName,
                            )
                        )
                    0L -> {}
                    else ->
                        throw IllegalStateException(
                            "Invalid minGenerationId ${writeConfig.minimumGenerationId} for stream ${writeConfig.streamName}. GenerationId=${writeConfig.generationId}"
                        )
                }
                log.info {
                    "Preparing staging area in destination completed for schema $schema stream $stream"
                }
            }

            typerDeduper.prepareFinalTables()

            log.info { "Executing finalization of tables." }
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
        stagedFiles: List<String>?,
        tableName: String?,
        schemaName: String?,
        stagingOperations: StagingOperations,
    ) {
        try {
            stagingOperations.copyIntoTableFromStage(
                database,
                stageName,
                stagingPath,
                stagedFiles,
                tableName,
                schemaName
            )
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
            _: Boolean,
            streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary> ->
            // After moving data from staging area to the target table (airybte_raw) clean up the
            // staging
            // area (if user configured)
            log.info { "Cleaning up destination started for ${writeConfigs.size} streams" }
            typerDeduper.typeAndDedupe(streamSyncSummaries)
            for (writeConfig in writeConfigs) {
                val schemaName = writeConfig.rawNamespace
                if (purgeStagingData) {
                    val stageName =
                        stagingOperations.getStageName(schemaName, writeConfig.rawTableName)
                    val stagePath =
                        stagingOperations.getStagingPath(
                            RANDOM_CONNECTION_ID,
                            schemaName,
                            writeConfig.streamName,
                            writeConfig.rawTableName,
                            writeConfig.writeDatetime
                        )
                    log.info {
                        "Cleaning stage in destination started for stream ${writeConfig.streamName}. schema $schemaName, stage: $stagePath"
                    }
                    // TODO: This is another weird manifestation of Redshift vs Snowflake using
                    // either or variables from
                    // stageName/StagingPath.
                    stagingOperations.dropStageIfExists(database, stageName, stagePath)
                }
            }
            typerDeduper.commitFinalTables(streamSyncSummaries)
            typerDeduper.cleanup()
            log.info { "Cleaning up destination completed." }
        }
    }
}
