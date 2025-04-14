/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.integrations.base.JavaBaseConstants.DestinationColumns.V2_WITH_GENERATION
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.cdk.integrations.destination.gcs.GcsNameTransformer
import io.airbyte.cdk.integrations.destination.gcs.GcsStorageOperations
import io.airbyte.cdk.integrations.destination.gcs.credential.GcsHmacKeyCredentialConfig
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.staging.operation.StagingStreamOperations
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.base.destination.operation.DefaultSyncOperation
import io.airbyte.integrations.base.destination.operation.StandardStreamOperation
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.migrators.BigQueryDV2Migration
import io.airbyte.integrations.destination.bigquery.migrators.BigQueryDestinationState
import io.airbyte.integrations.destination.bigquery.migrators.BigqueryAirbyteMetaAndGenerationIdMigration
import io.airbyte.integrations.destination.bigquery.operation.BigQueryDirectLoadingStorageOperation
import io.airbyte.integrations.destination.bigquery.operation.BigQueryGcsStorageOperation
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.GcsFilePostProcessing
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import jakarta.inject.Singleton

@Singleton
class BigqueryWriter(
    private val bigquery: BigQuery,
    private val config: BigqueryConfiguration,
    private val sqlGenerator: BigQuerySqlGenerator,
    private val parsedCatalog: ParsedCatalog,
    private val destinationHandler: BigQueryDestinationHandler,
) : DestinationWriter {
    private lateinit var syncOperation: DefaultSyncOperation<BigQueryDestinationState>

    override suspend fun setup() {
        super.setup()

        val migrations =
            listOf(
                BigQueryDV2Migration(sqlGenerator, bigquery),
                BigqueryAirbyteMetaAndGenerationIdMigration(bigquery),
            )
        syncOperation =
            when (config.loadingMethod) {
                is BatchedStandardInsertConfiguration -> {
                    val bigQueryLoadingStorageOperation =
                        BigQueryDirectLoadingStorageOperation(
                            bigquery,
                            bigQueryClientChunkSize = null,
                            BigQueryRecordFormatter(),
                            sqlGenerator,
                            destinationHandler,
                            config.datasetLocation.region,
                        )
                    DefaultSyncOperation(
                        parsedCatalog,
                        destinationHandler,
                        config.datasetId,
                        {
                            initialStatus: DestinationInitialStatus<BigQueryDestinationState>,
                            disableTD ->
                            StandardStreamOperation(
                                bigQueryLoadingStorageOperation,
                                initialStatus,
                                disableTD,
                            )
                        },
                        migrations,
                        config.disableTypingDeduping,
                    )
                }
                is GcsStagingConfiguration -> {
                    val gcsNameTransformer = GcsNameTransformer()
                    // TODO validate this
                    val gcsConfig = BigQueryUtils.getGcsCsvDestinationConfig(config)
                    GcsDestinationConfig(
                        config.loadingMethod.gcsClientConfig.gcsBucketName,
                        bucketPath = config.loadingMethod.gcsClientConfig.path,
                        bucketRegion = config.datasetLocation.region,
                        gcsCredentialConfig = GcsHmacKeyCredentialConfig(),
                        formatConfig = TODO(),
                    )
                    val keepStagingFiles =
                        config.loadingMethod.filePostProcessing == GcsFilePostProcessing.KEEP
                    val gcsOperations =
                        GcsStorageOperations(gcsNameTransformer, gcsConfig.getS3Client(), gcsConfig)
                    val bigQueryGcsStorageOperations =
                        BigQueryGcsStorageOperation(
                            gcsOperations,
                            gcsConfig,
                            gcsNameTransformer,
                            keepStagingFiles,
                            bigquery,
                            sqlGenerator,
                            destinationHandler,
                        )
                    DefaultSyncOperation(
                        parsedCatalog,
                        destinationHandler,
                        config.datasetId,
                        {
                            initialStatus: DestinationInitialStatus<BigQueryDestinationState>,
                            disableTD ->
                            StagingStreamOperations(
                                bigQueryGcsStorageOperations,
                                initialStatus,
                                FileUploadFormat.CSV,
                                V2_WITH_GENERATION,
                                disableTD,
                            )
                        },
                        migrations,
                        config.disableTypingDeduping,
                    )
                }
            }
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return BigqueryStreamLoader(stream, bigquery, config)
    }
}

// TODO delete this - this is definitely duplicated code, and also is definitely wrong
//   e.g. we need to handle special chars in stream name/namespace (c.f.
// bigquerysqlgenerator.buildStreamId)
//   and that logic needs to be in BigqueryWriter.setup, to handle collisions
//   (probably actually a toolkit)
object TempUtils {
    fun rawTableId(
        config: BigqueryConfiguration,
        streamDescriptor: DestinationStream.Descriptor,
    ) =
        TableId.of(
            config.rawTableDataset,
            StreamId.concatenateRawTableName(
                streamDescriptor.namespace ?: config.datasetId,
                streamDescriptor.name
            )
        )
}
