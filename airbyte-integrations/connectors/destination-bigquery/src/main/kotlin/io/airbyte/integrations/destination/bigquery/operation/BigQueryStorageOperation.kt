/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.operation

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.TableResult
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.integrations.base.destination.operation.StorageOperation
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.util.Optional
import java.util.concurrent.ConcurrentHashMap

private val log = KotlinLogging.logger {}

abstract class BigQueryStorageOperation<Data>(
    protected val bigquery: BigQuery,
    private val sqlGenerator: BigQuerySqlGenerator,
    private val destinationHandler: BigQueryDestinationHandler,
    protected val datasetLocation: String
) : StorageOperation<Data> {
    private val existingSchemas = ConcurrentHashMap.newKeySet<String>()
    override fun prepareStage(streamId: StreamId, suffix: String, replace: Boolean) {
        // Prepare staging table. For overwrite, it does drop-create so we can skip explicit create.
        if (replace) {
            truncateStagingTable(streamId, suffix)
        } else {
            createStagingTable(streamId, suffix)
        }
    }

    override fun overwriteStage(streamId: StreamId, suffix: String) {
        if (suffix == "") {
            throw IllegalArgumentException("Cannot overwrite raw table with empty suffix")
        }
        bigquery.delete(tableId(streamId, ""))
        bigquery.query(
            QueryJobConfiguration.of(
                """ALTER TABLE `${streamId.rawNamespace}`.`${streamId.rawName}$suffix` RENAME TO `${streamId.rawName}`"""
            ),
        )
    }

    override fun transferFromTempStage(streamId: StreamId, suffix: String) {
        if (suffix == "") {
            throw IllegalArgumentException(
                "Cannot transfer records from temp raw table with empty suffix"
            )
        }
        // TODO figure out how to make this work
        // something about incompatible partitioning spec (probably b/c we're copying from a temp
        // table partitioned on generation ID into an old real raw table partitioned on
        // extracted_at)
        val tempRawTable = tableId(streamId, suffix)
        //        val jobConf =
        //            CopyJobConfiguration.newBuilder(tableId(streamId, ""), tempRawTable)
        //                .setWriteDisposition(JobInfo.WriteDisposition.WRITE_APPEND)
        //                .build()
        //        val job = bigquery.create(JobInfo.of(jobConf))
        //        BigQueryUtils.waitForJobFinish(job)

        bigquery.query(
            QueryJobConfiguration.of(
                """
                    INSERT INTO `${streamId.rawNamespace}`.`${streamId.rawName}`
                    SELECT * FROM `${streamId.rawNamespace}`.`${streamId.rawName}$suffix`
                """.trimIndent()
            )
        )
        bigquery.delete(tempRawTable)
    }

    override fun getStageGeneration(streamId: StreamId, suffix: String): Long? {
        val result: TableResult =
            bigquery.query(
                QueryJobConfiguration.of(
                    "SELECT _airbyte_generation_id FROM ${streamId.rawNamespace}.${streamId.rawName}$suffix LIMIT 1"
                ),
            )
        if (result.totalRows == 0L) {
            return null
        }
        val value = result.iterateAll().first().get(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID)
        return if (value == null || value.isNull) {
            0
        } else {
            value.longValue
        }
    }

    private fun createStagingTable(streamId: StreamId, suffix: String) {
        BigQueryUtils.createPartitionedTableIfNotExists(
            bigquery,
            tableId(streamId, suffix),
            BigQueryRecordFormatter.SCHEMA_V2,
        )
    }

    private fun dropStagingTable(streamId: StreamId, suffix: String) {
        bigquery.delete(tableId(streamId, suffix))
    }

    /**
     * "Truncates" table, this is a workaround to the issue with TRUNCATE TABLE in BigQuery where
     * the table's partition filter must be turned off to truncate. Since deleting a table is a free
     * operation this option re-uses functions that already exist
     */
    private fun truncateStagingTable(streamId: StreamId, suffix: String) {
        val tableId = TableId.of(streamId.rawNamespace, streamId.rawName)
        log.info { "Truncating raw table $tableId" }
        dropStagingTable(streamId, suffix)
        createStagingTable(streamId, suffix)
    }

    override fun cleanupStage(streamId: StreamId) {
        log.info { "Nothing to cleanup in stage for Streaming inserts" }
    }

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
        if (tmpTableSuffix == "") {
            throw IllegalArgumentException("Cannot overwrite final table with empty suffix")
        }
        log.info {
            "Overwriting table ${streamConfig.id.finalTableId(BigQuerySqlGenerator.QUOTE)} with ${
                streamConfig.id.finalTableId(
                    BigQuerySqlGenerator.QUOTE,
                    tmpTableSuffix,
                )
            }"
        }
        destinationHandler.execute(
            sqlGenerator.overwriteFinalTable(streamConfig.id, tmpTableSuffix),
        )
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

    companion object {
        fun tableId(streamId: StreamId, suffix: String = ""): TableId =
            TableId.of(streamId.rawNamespace, streamId.rawName + suffix)
    }
}
