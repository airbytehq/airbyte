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
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.legacy_typing_deduping.TypingDedupingFinalTableOperations
import io.airbyte.cdk.load.orchestration.legacy_typing_deduping.TypingDedupingWriter
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
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class BigqueryWriterFactory(
    private val catalog: DestinationCatalog,
    private val bigquery: BigQuery,
    private val config: BigqueryConfiguration,
    private val sqlGenerator: BigQuerySqlGenerator,
    private val destinationHandler: BigQueryDestinationHandler,
) {
    @Singleton
    fun make() = TypingDedupingWriter(
        catalog,
        BigqueryInitialStateGatherer(),
        BigqueryRawTableOperations(),
        TypingDedupingFinalTableOperations(sqlGenerator, destinationHandler),
    )
}

// TODO delete this - this is definitely duplicated code, and also is definitely wrong
//   e.g. we need to handle special chars in stream name/namespace (c.f.
//   bigquerysqlgenerator.buildStreamId)
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
