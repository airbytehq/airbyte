/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.api.gax.retrying.RetrySettings
import com.google.auth.oauth2.GoogleCredentials
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryOptions
import io.airbyte.cdk.load.check.DestinationCheckerSync
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableWriter
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.NoopTypingDedupingSqlGenerator
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingExecutionConfig
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingFinalTableOperations
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingWriter
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.cdk.load.write.WriteOperation
import io.airbyte.integrations.destination.bigquery.check.BigqueryCheckCleaner
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryBulkOneShotUploader
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryBulkOneShotUploaderStep
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigqueryBulkLoadConfiguration
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigqueryConfiguredForBulkLoad
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigQueryDatabaseHandler
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadDatabaseInitialStatusGatherer
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadSqlGenerator
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryTableOperationsClient
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryTableSchemaEvolutionClient
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.legacy_raw_tables.BigqueryRawTableOperations
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.legacy_raw_tables.BigqueryTypingDedupingDatabaseInitialStatusGatherer
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream
import java.io.InputStream
import java.io.OutputStream
import java.nio.charset.StandardCharsets

private val logger = KotlinLogging.logger {}

@Factory
class BigqueryBeansFactory {
    @Singleton fun getConfig(config: DestinationConfiguration) = config as BigqueryConfiguration

    @Singleton
    @Requires(condition = BigqueryConfiguredForBulkLoad::class)
    fun getBulkLoadConfig(config: BigqueryConfiguration) = BigqueryBulkLoadConfiguration(config)

    @Singleton
    @Named("bigQueryOneShotStep")
    @Requires(condition = BigqueryConfiguredForBulkLoad::class)
    @Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
    fun <O : OutputStream> getBigQueryOneShotStep(
        bigQueryOneShotUploader: BigQueryBulkOneShotUploader<O>,
        taskFactory: io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory,
        @Named("numInputPartitions") numInputPartitions: Int,
    ): BigQueryBulkOneShotUploaderStep<io.airbyte.cdk.load.message.StreamKey, O> {
        return BigQueryBulkOneShotUploaderStep(
            bigQueryOneShotUploader,
            taskFactory,
            numInputPartitions
        )
    }

    @Singleton
    @Named("checkNamespace")
    fun getCheckNamespace(config: BigqueryConfiguration): String = config.datasetId

    @Singleton
    fun getChecker(
        catalog: DestinationCatalog,
        @Named("inputStream") stdinPipe: InputStream,
        taskLauncher: DestinationTaskLauncher,
        syncManager: SyncManager,
    ) =
        DestinationCheckerSync(
            catalog,
            stdinPipe,
            WriteOperation(taskLauncher, syncManager),
            BigqueryCheckCleaner(),
        )

    @Singleton
    fun getWriter(
        bigquery: BigQuery,
        config: BigqueryConfiguration,
        names: TableCatalog,
        // micronaut will only instantiate a single instance of StreamStateStore,
        // so accept it as a * generic and cast as needed.
        // we use a different type depending on whether we're in legacy raw tables vs
        // direct-load tables mode.
        streamStateStore: StreamStateStore<*>,
    ): DestinationWriter {
        val destinationHandler = BigQueryDatabaseHandler(bigquery, config.datasetLocation.region)
        if (config.legacyRawTablesOnly) {
            // force smart cast
            @Suppress("UNCHECKED_CAST")
            streamStateStore as StreamStateStore<TypingDedupingExecutionConfig>
            return TypingDedupingWriter(
                names,
                BigqueryTypingDedupingDatabaseInitialStatusGatherer(bigquery),
                destinationHandler,
                BigqueryRawTableOperations(bigquery),
                TypingDedupingFinalTableOperations(
                    NoopTypingDedupingSqlGenerator,
                    destinationHandler,
                ),
                disableTypeDedupe = true,
                streamStateStore = streamStateStore,
            )
        } else {
            val tableOperations =
                BigqueryTableOperationsClient(
                    BigqueryDirectLoadSqlGenerator(
                        projectId = config.projectId,
                        cdcDeletionMode = config.cdcDeletionMode,
                    ),
                    destinationHandler,
                    bigquery,
                )
            // force smart cast
            @Suppress("UNCHECKED_CAST")
            streamStateStore as StreamStateStore<DirectLoadTableExecutionConfig>
            val tempTableNameGenerator =
                DefaultTempTableNameGenerator(internalNamespace = config.internalTableDataset)

            return DirectLoadTableWriter(
                internalNamespace = config.internalTableDataset,
                names = names,
                stateGatherer =
                    BigqueryDirectLoadDatabaseInitialStatusGatherer(
                        bigquery,
                        tempTableNameGenerator
                    ),
                destinationHandler = destinationHandler,
                schemaEvolutionClient =
                    BigqueryTableSchemaEvolutionClient(
                        bigquery,
                        tableOperations,
                        destinationHandler,
                        projectId = config.projectId,
                        tempTableNameGenerator,
                    ),
                tableOperationsClient = tableOperations,
                streamStateStore = streamStateStore,
                tempTableNameGenerator,
            )
        }
    }

    @Singleton
    fun getBigqueryClient(config: BigqueryConfiguration): BigQuery {
        // Follows this order of resolution:
        // https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault
        val credentials =
            if (config.credentialsJson == null) {
                logger.info {
                    "No service account key json is provided. It is required if you are using Airbyte cloud."
                }
                logger.info { "Using the default service account credential from environment." }
                GoogleCredentials.getApplicationDefault()
            } else {
                // The JSON credential can either be a raw JSON object, or a serialized JSON object.
                GoogleCredentials.fromStream(
                    ByteArrayInputStream(
                        config.credentialsJson.toByteArray(StandardCharsets.UTF_8)
                    ),
                )
            }
        return BigQueryOptions.newBuilder()
            .setProjectId(config.projectId)
            .setCredentials(credentials)
            .setHeaderProvider(BigQueryUtils.headerProvider)
            .setRetrySettings(
                RetrySettings.newBuilder()
                    // Most of the values are default. We need to override them all if we want to
                    // set a different value for `setMaxAttempts`..............
                    .setInitialRetryDelayDuration(java.time.Duration.ofMillis(1000L))
                    .setMaxRetryDelayDuration(java.time.Duration.ofMillis(32_000L))
                    .setTotalTimeoutDuration(java.time.Duration.ofMillis(60_000L))
                    .setInitialRpcTimeoutDuration(java.time.Duration.ofMillis(50_000L))
                    .setRpcTimeoutMultiplier(1.0)
                    .setMaxRpcTimeoutDuration(java.time.Duration.ofMillis(50_000L))
                    .setMaxAttempts(15)
                    .setRetryDelayMultiplier(1.5)
                    .build()
            )
            .build()
            .service
    }
}
