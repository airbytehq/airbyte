/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.operation

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.TableId
import io.airbyte.integrations.base.destination.operation.StorageOperation
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.util.*
import java.util.concurrent.ConcurrentHashMap

private val log = KotlinLogging.logger {}

abstract class BigQueryStorageOperation<Data>(
    protected val bigquery: BigQuery,
    private val sqlGenerator: BigQuerySqlGenerator,
    private val destinationHandler: BigQueryDestinationHandler,
    protected val datasetLocation: String
) : StorageOperation<Data> {
    private val existingSchemas = ConcurrentHashMap.newKeySet<String>()
    override fun prepareStage(streamId: StreamId, destinationSyncMode: DestinationSyncMode) {
        // Prepare staging table. For overwrite, it does drop-create so we can skip explicit create.
        if (destinationSyncMode == DestinationSyncMode.OVERWRITE) {
            truncateStagingTable(streamId)
        } else {
            createStagingTable(streamId)
        }
    }

    private fun createStagingTable(streamId: StreamId) {
        val tableId = TableId.of(streamId.rawNamespace, streamId.rawName)
        BigQueryUtils.createPartitionedTableIfNotExists(
            bigquery,
            tableId,
            BigQueryRecordFormatter.SCHEMA_V2
        )
    }

    private fun dropStagingTable(streamId: StreamId) {
        val tableId = TableId.of(streamId.rawNamespace, streamId.rawName)
        bigquery.delete(tableId)
    }

    /**
     * "Truncates" table, this is a workaround to the issue with TRUNCATE TABLE in BigQuery where
     * the table's partition filter must be turned off to truncate. Since deleting a table is a free
     * operation this option re-uses functions that already exist
     */
    private fun truncateStagingTable(streamId: StreamId) {
        val tableId = TableId.of(streamId.rawNamespace, streamId.rawName)
        log.info { "Truncating raw table $tableId" }
        dropStagingTable(streamId)
        createStagingTable(streamId)
    }

    override fun cleanupStage(streamId: StreamId) {
        log.info { "Nothing to cleanup in stage for Streaming inserts" }
    }

    abstract override fun writeToStage(streamId: StreamId, data: Data)

    override fun createFinalTable(streamConfig: StreamConfig, suffix: String, replace: Boolean) {
        destinationHandler.execute(sqlGenerator.createTable(streamConfig, suffix, replace))
    }

    override fun softResetFinalTable(streamConfig: StreamConfig) {
        TyperDeduperUtil.executeSoftReset(
            sqlGenerator = sqlGenerator,
            destinationHandler = destinationHandler,
            streamConfig,
        )
    }

    override fun overwriteFinalTable(streamConfig: StreamConfig, tmpTableSuffix: String) {
        if (tmpTableSuffix.isNotBlank()) {
            log.info {
                "Overwriting table ${streamConfig.id.finalTableId(BigQuerySqlGenerator.QUOTE)} with ${
                    streamConfig.id.finalTableId(
                        BigQuerySqlGenerator.QUOTE,
                        tmpTableSuffix,
                    )
                }"
            }
            destinationHandler.execute(
                sqlGenerator.overwriteFinalTable(streamConfig.id, tmpTableSuffix)
            )
        }
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
            finalTableSuffix,
        )
    }
}
