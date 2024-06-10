/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.operation

import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.integrations.base.destination.operation.StorageOperation
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil
import io.airbyte.integrations.destination.snowflake.SnowflakeSQLNameTransformer
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.util.*

private val log = KotlinLogging.logger {}

class SnowflakeStorageOperation(
    private val sqlGenerator: SnowflakeSqlGenerator,
    private val destinationHandler: SnowflakeDestinationHandler,
    private val retentionPeriodDays: Int,
    private val staging: SnowflakeStagingClient,
    private val nameTransformer: StandardNameTransformer = SnowflakeSQLNameTransformer(),
) : StorageOperation<SerializableBuffer> {

    private val connectionId = UUID.randomUUID()
    private val syncDateTime = Instant.now()

    override fun prepareStage(streamId: StreamId, destinationSyncMode: DestinationSyncMode) {
        // create raw table
        destinationHandler.execute(Sql.of(createTableQuery(streamId)))
        if (destinationSyncMode == DestinationSyncMode.OVERWRITE) {
            destinationHandler.execute(Sql.of(truncateTableQuery(streamId)))
        }
        // create stage
        staging.createStageIfNotExists(getStageName(streamId))
    }

    internal fun createTableQuery(streamId: StreamId): String {
        return """
        |CREATE TABLE IF NOT EXISTS "${streamId.rawNamespace}"."${streamId.rawName}"( 
        |   "${JavaBaseConstants.COLUMN_NAME_AB_RAW_ID}" VARCHAR PRIMARY KEY,
        |   "${JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT}" TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp(),
        |   "${JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT}" TIMESTAMP WITH TIME ZONE DEFAULT NULL,
        |   "${JavaBaseConstants.COLUMN_NAME_DATA}" VARIANT
        |) data_retention_time_in_days = $retentionPeriodDays;
        """.trimMargin()
    }

    internal fun truncateTableQuery(streamId: StreamId): String {
        return "TRUNCATE TABLE \"${streamId.rawNamespace}\".\"${streamId.rawName}\";\n"
    }

    override fun writeToStage(streamId: StreamId, data: SerializableBuffer) {
        val stageName = getStageName(streamId)
        val stagingPath = getStagingPath()
        val stagedFileName = staging.uploadRecordsToStage(data, stageName, stagingPath)
        staging.copyIntoTableFromStage(stageName, stagingPath, listOf(stagedFileName), streamId)
    }
    override fun cleanupStage(streamId: StreamId) {
        val stageName = getStageName(streamId)
        log.info { "Cleaning up stage $stageName" }
        staging.dropStageIfExists(stageName)
    }

    internal fun getStageName(streamId: StreamId): String {
        return """
            "${nameTransformer.convertStreamName(streamId.rawNamespace)}"."${ nameTransformer.convertStreamName(streamId.rawName)}"
        """.trimIndent()
    }

    private fun getStagingPath(): String {
        // see https://docs.snowflake.com/en/user-guide/data-load-considerations-stage.html
        val zonedDateTime = ZonedDateTime.ofInstant(syncDateTime, ZoneOffset.UTC)
        return nameTransformer.applyDefaultCase(
            String.format(
                "%s/%02d/%02d/%02d/%s/",
                zonedDateTime.year,
                zonedDateTime.monthValue,
                zonedDateTime.dayOfMonth,
                zonedDateTime.hour,
                connectionId
            )
        )
    }

    override fun createFinalTable(streamConfig: StreamConfig, suffix: String, replace: Boolean) {
        destinationHandler.execute(sqlGenerator.createTable(streamConfig, suffix, replace))
    }

    override fun overwriteFinalTable(streamConfig: StreamConfig, tmpTableSuffix: String) {
        if (tmpTableSuffix.isNotBlank()) {
            log.info {
                "Overwriting table ${streamConfig.id.finalTableId(SnowflakeSqlGenerator.QUOTE)} with ${
                    streamConfig.id.finalTableId(
                        SnowflakeSqlGenerator.QUOTE,
                        tmpTableSuffix,
                    )
                }"
            }
            destinationHandler.execute(
                sqlGenerator.overwriteFinalTable(streamConfig.id, tmpTableSuffix)
            )
        }
    }

    override fun softResetFinalTable(streamConfig: StreamConfig) {
        TyperDeduperUtil.executeSoftReset(sqlGenerator, destinationHandler, streamConfig)
    }

    override fun typeAndDedupe(
        streamConfig: StreamConfig,
        maxProcessedTimestamp: Optional<Instant>,
        finalTableSuffix: String
    ) {
        TyperDeduperUtil.executeTypeAndDedupe(
            sqlGenerator = sqlGenerator,
            destinationHandler = destinationHandler,
            streamConfig,
            maxProcessedTimestamp,
            finalTableSuffix
        )
    }
}
