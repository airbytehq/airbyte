/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.CopyJobConfiguration
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.QueryJobConfiguration
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DefaultDirectLoadTableSqlOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.toTableId

class BigqueryDirectLoadSqlTableOperations(
    private val defaultOperations: DefaultDirectLoadTableSqlOperations,
    private val bq: BigQuery,
    private val jobProjectId: String,
    private val datasetLocation: String,
    private val emptiesDroppedTables: Boolean = false,
) : DirectLoadTableSqlOperations by defaultOperations {
    /**
     * The tables dropped here are temp tables, and the next sync creates each again under its name.
     * The Storage Write API does not find a table dropped and created again under the same name for
     * minutes, so with it they are emptied instead and keep their identity.
     */
    override suspend fun dropTable(tableName: TableName) {
        if (!emptiesDroppedTables) {
            defaultOperations.dropTable(tableName)
            return
        }
        val table = bq.getTable(tableName.toTableId()) ?: return
        val tableId = table.tableId
        val job =
            bq.create(
                JobInfo.of(
                    JobId.newBuilder()
                        .setProject(jobProjectId)
                        .setLocation(datasetLocation)
                        .setRandomJob()
                        .build(),
                    QueryJobConfiguration.of(
                        "TRUNCATE TABLE `${tableId.project}`.`${tableId.dataset}`.`${tableId.table}`",
                    ),
                ),
            )
        BigQueryUtils.waitForJobFinish(job)
    }

    @SuppressFBWarnings("RV_RETURN_VALUE_IGNORED_NO_SIDE_EFFECT", "kotlin coroutines")
    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        // manually delete the target table - otherwise we can't e.g. update the partitioning scheme
        bq.getTable(targetTableName.toTableId())?.delete()

        // Bigquery's SQL `ALTER TABLE RENAME TO` statement doesn't support moving tables
        // across datasets.
        // So we'll use a Copy job instead.
        // (this is more efficient than just `insert into tgt select * from src`)
        val sourceTableId = sourceTableName.toTableId()
        val jobId =
            JobId.newBuilder()
                .setProject(jobProjectId)
                .setLocation(datasetLocation)
                .setRandomJob()
                .build()
        val job =
            bq.create(
                JobInfo.of(
                    jobId,
                    CopyJobConfiguration.newBuilder(
                            targetTableName.toTableId(),
                            sourceTableId,
                        )
                        // create the table if it doesn't yet exist
                        .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
                        // overwrite the table if it already exists
                        .setWriteDisposition(JobInfo.WriteDisposition.WRITE_TRUNCATE)
                        .build(),
                ),
            )
        BigQueryUtils.waitForJobFinish(job)
        bq.getTable(sourceTableId).delete()
    }
}
