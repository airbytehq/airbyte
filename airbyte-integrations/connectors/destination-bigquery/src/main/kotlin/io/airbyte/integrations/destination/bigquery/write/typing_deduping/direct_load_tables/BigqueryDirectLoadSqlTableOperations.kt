/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.CopyJobConfiguration
import com.google.cloud.bigquery.JobInfo
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DefaultDirectLoadTableSqlOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.toTableId

class BigqueryDirectLoadSqlTableOperations(
    private val defaultOperations: DefaultDirectLoadTableSqlOperations,
    private val bq: BigQuery,
) : DirectLoadTableSqlOperations by defaultOperations {
    @SuppressFBWarnings("RV_RETURN_VALUE_IGNORED_NO_SIDE_EFFECT", "kotlin coroutines")
    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        // manually delete the target table - otherwise we can't e.g. update the partitioning scheme
        bq.getTable(targetTableName.toTableId())?.delete()

        // Bigquery's SQL `ALTER TABLE RENAME TO` statement doesn't support moving tables
        // across datasets.
        // So we'll use a Copy job instead.
        // (this is more efficient than just `insert into tgt select * from src`)
        val sourceTableId = sourceTableName.toTableId()
        val job =
            bq.create(
                JobInfo.of(
                    CopyJobConfiguration.newBuilder(
                            targetTableName.toTableId(),
                            sourceTableId,
                        )
                        // create the table if it doesn't yet exist
                        .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
                        // overwrite the table if it already exists
                        .setWriteDisposition(JobInfo.WriteDisposition.WRITE_TRUNCATE)
                        .build()
                )
            )
        BigQueryUtils.waitForJobFinish(job)
        bq.getTable(sourceTableId).delete()
    }
}
