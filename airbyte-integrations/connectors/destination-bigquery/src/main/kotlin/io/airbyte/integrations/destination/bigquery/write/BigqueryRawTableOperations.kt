/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.TableResult
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingRawTableOperations
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

class BigqueryRawTableOperations(private val bigquery: BigQuery) :
    TypingDedupingRawTableOperations {
    override fun prepareRawTable(rawTableName: TableName, suffix: String, replace: Boolean) {
        // Prepare staging table. For overwrite, it does drop-create so we can skip explicit create.
        if (replace) {
            truncateStagingTable(rawTableName, suffix)
        } else {
            createStagingTable(rawTableName, suffix)
        }
    }

    override fun overwriteRawTable(rawTableName: TableName, suffix: String) {
        if (suffix == "") {
            throw IllegalArgumentException("Cannot overwrite raw table with empty suffix")
        }
        bigquery.delete(tableId(rawTableName, ""))
        bigquery.query(
            QueryJobConfiguration.of(
                """ALTER TABLE `${rawTableName.namespace}`.`${rawTableName.name}$suffix` RENAME TO `${rawTableName.name}`"""
            ),
        )
    }

    override fun transferFromTempRawTable(rawTableName: TableName, suffix: String) {
        if (suffix == "") {
            throw IllegalArgumentException(
                "Cannot transfer records from temp raw table with empty suffix"
            )
        }
        // TODO figure out how to make this work
        // something about incompatible partitioning spec (probably b/c we're copying from a temp
        // table partitioned on generation ID into an old real raw table partitioned on
        // extracted_at)
        val tempRawTable = tableId(rawTableName, suffix)
        //        val jobConf =
        //            CopyJobConfiguration.newBuilder(tableId(streamId, ""), tempRawTable)
        //                .setWriteDisposition(JobInfo.WriteDisposition.WRITE_APPEND)
        //                .build()
        //        val job = bigquery.create(JobInfo.of(jobConf))
        //        BigQueryUtils.waitForJobFinish(job)

        bigquery.query(
            QueryJobConfiguration.of(
                """
                INSERT INTO `${rawTableName.namespace}`.`${rawTableName.name}`
                SELECT * FROM `${rawTableName.namespace}`.`${rawTableName.name}$suffix`
                """.trimIndent()
            )
        )
        bigquery.delete(tempRawTable)
    }

    override fun getRawTableGeneration(rawTableName: TableName, suffix: String): Long? {
        val result: TableResult =
            bigquery.query(
                QueryJobConfiguration.of(
                    "SELECT _airbyte_generation_id FROM ${rawTableName.namespace}.${rawTableName.name}$suffix LIMIT 1"
                ),
            )
        if (result.totalRows == 0L) {
            return null
        }
        val value = result.iterateAll().first().get(Meta.COLUMN_NAME_AB_GENERATION_ID)
        return if (value == null || value.isNull) {
            0
        } else {
            value.longValue
        }
    }

    private fun createStagingTable(rawTableName: TableName, suffix: String) {
        BigQueryUtils.createPartitionedTableIfNotExists(
            bigquery,
            tableId(rawTableName, suffix),
            BigQueryRecordFormatter.SCHEMA_V2,
        )
    }

    private fun dropStagingTable(rawTableName: TableName, suffix: String) {
        bigquery.delete(tableId(rawTableName, suffix))
    }

    /**
     * "Truncates" table, this is a workaround to the issue with TRUNCATE TABLE in BigQuery where
     * the table's partition filter must be turned off to truncate. Since deleting a table is a free
     * operation this option re-uses functions that already exist
     */
    private fun truncateStagingTable(rawTableName: TableName, suffix: String) {
        logger.info { "Truncating raw table ${tableId(rawTableName, suffix)}" }
        dropStagingTable(rawTableName, suffix)
        createStagingTable(rawTableName, suffix)
    }

    private fun tableId(rawTableName: TableName, suffix: String = ""): TableId =
        TableId.of(rawTableName.namespace, rawTableName.name + suffix)
}
