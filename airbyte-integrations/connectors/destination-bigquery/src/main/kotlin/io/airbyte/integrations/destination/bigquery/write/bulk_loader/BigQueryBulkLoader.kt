/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import com.google.cloud.bigquery.*
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.LoadJobConfiguration
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.file.gcs.GcsClient
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogByDescriptor
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.cdk.load.write.db.BulkLoader
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.GcsFilePostProcessing
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.toTableId
import io.micronaut.context.annotation.Requires
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import jakarta.inject.Singleton

class BigQueryBulkLoader(
    private val storageClient: GcsClient,
    private val bigQueryClient: BigQuery,
    private val bigQueryConfiguration: BigqueryConfiguration,
    private val tableId: TableId,
    private val schema: Schema,
) : BulkLoader<GcsBlob> {
    override suspend fun load(remoteObject: GcsBlob) {
        val gcsUri = "gs://${remoteObject.storageConfig.gcsBucketName}/${remoteObject.key}"

        val csvOptions =
            CsvOptions.newBuilder()
                .setSkipLeadingRows(1)
                .setAllowQuotedNewLines(true) // safe for long JSON strings
                .setAllowJaggedRows(true)
                .build()

        val configuration =
            LoadJobConfiguration.builder(tableId, gcsUri)
                .setFormatOptions(csvOptions)
                .setSchema(schema)
                .setWriteDisposition(JobInfo.WriteDisposition.WRITE_APPEND)
                .setJobTimeoutMs(600000L) // 10 min timeout
                .build()

        val loadJob = bigQueryClient.create(JobInfo.of(configuration))

        try {
            BigQueryUtils.waitForJobFinish(loadJob)
        } catch (e: Exception) {
            throw RuntimeException(
                "Failed to load CSV data from $gcsUri to table ${tableId.dataset}.${tableId.table}",
                e
            )
        }

        val loadingMethodPostProcessing =
            (bigQueryConfiguration.loadingMethod as GcsStagingConfiguration).filePostProcessing
        if (loadingMethodPostProcessing == GcsFilePostProcessing.DELETE) {
            storageClient.delete(remoteObject)
        }
    }

    override fun close() {
        /* Do nothing */
    }
}

class BigqueryConfiguredForBulkLoad : Condition {
    override fun matches(context: ConditionContext<*>): Boolean {
        val config = context.beanContext.getBean(BigqueryConfiguration::class.java)
        return config.loadingMethod is GcsStagingConfiguration
    }
}

@Singleton
@Requires(condition = BigqueryConfiguredForBulkLoad::class)
class BigQueryBulkLoaderFactory(
    private val catalog: DestinationCatalog,
    private val names: TableCatalogByDescriptor,
    private val storageClient: GcsClient,
    private val bigQueryClient: BigQuery,
    private val bigQueryConfiguration: BigqueryConfiguration,
    private val typingDedupingExecutionConfigStreamStateStore:
        StreamStateStore<TypingDedupingExecutionConfig>?,
    private val directLoadStreamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>?,
) : BulkLoaderFactory<StreamKey, GcsBlob> {
    override val numPartWorkers: Int = 2
    override val numUploadWorkers: Int = 10
    override val maxNumConcurrentLoads: Int = 1

    override val objectSizeBytes: Long = 200 * 1024 * 1024 // 200 MB
    override val partSizeBytes: Long = 10 * 1024 * 1024 // 10 MB
    override val maxMemoryRatioReservedForParts: Double = 0.6

    override fun create(key: StreamKey, partition: Int): BulkLoader<GcsBlob> {
        val tableId: TableId
        val schema: Schema
        val tableNameInfo = names[key.stream]!!
        if (bigQueryConfiguration.legacyRawTablesOnly) {
            val rawTableName = tableNameInfo.tableNames.rawTableName!!
            val rawTableSuffix =
                typingDedupingExecutionConfigStreamStateStore!!.get(key.stream)!!.rawTableSuffix
            tableId = TableId.of(rawTableName.namespace, rawTableName.name + rawTableSuffix)
            schema = BigQueryRecordFormatter.CSV_SCHEMA
        } else {
            tableId = directLoadStreamStateStore!!.get(key.stream)!!.tableName.toTableId()
            schema =
                BigQueryRecordFormatter.getDirectLoadSchema(
                    catalog.getStream(key.stream),
                    tableNameInfo.columnNameMapping,
                )
        }
        return BigQueryBulkLoader(
            storageClient,
            bigQueryClient,
            bigQueryConfiguration,
            tableId,
            schema,
        )
    }
}
