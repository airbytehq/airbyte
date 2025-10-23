/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.CopyJobConfiguration
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.QueryJobConfiguration
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.DatabaseHandler
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadSqlGenerator
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.toTableId
import jakarta.inject.Singleton

@Singleton
class BigqueryTableOperationsClient(
    private val generator: DirectLoadSqlGenerator,
    private val handler: DatabaseHandler,
    private val bigquery: BigQuery,
) : TableOperationsClient {
    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ) {
        handler.execute(
            generator.createTable(stream, tableName, columnNameMapping, replace = replace)
        )
    }

    @SuppressFBWarnings("RV_RETURN_VALUE_IGNORED_NO_SIDE_EFFECT", "kotlin coroutines")
    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        // manually delete the target table - otherwise we can't e.g. update the partitioning scheme
        bigquery.getTable(targetTableName.toTableId())?.delete()

        // Bigquery's SQL `ALTER TABLE RENAME TO` statement doesn't support moving tables
        // across datasets.
        // So we'll use a Copy job instead.
        // (this is more efficient than just `insert into tgt select * from src`)
        val sourceTableId = sourceTableName.toTableId()
        val job =
            bigquery.create(
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
        bigquery.getTable(sourceTableId).delete()
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        handler.execute(
            generator.copyTable(
                columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName,
            )
        )
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        handler.execute(
            generator.upsertTable(
                stream,
                columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName,
            )
        )
    }

    override suspend fun dropTable(tableName: TableName) {
        handler.execute(generator.dropTable(tableName))
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        val result =
            bigquery.query(
                QueryJobConfiguration.of(
                    "SELECT _airbyte_generation_id FROM `${tableName.namespace}`.`${tableName.name}` LIMIT 1",
                ),
            )
        val value = result.iterateAll().first().get(Meta.COLUMN_NAME_AB_GENERATION_ID)
        return if (value.isNull) {
            0
        } else {
            value.longValue
        }
    }
}
