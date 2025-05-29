/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.auth.oauth2.GoogleCredentials
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryOptions
import io.airbyte.cdk.load.check.DestinationCheckerSync
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingExecutionConfig
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingFinalTableOperations
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingWriter
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.cdk.load.write.WriteOperation
import io.airbyte.integrations.destination.bigquery.check.BigqueryCheckCleaner
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDatabaseHandler
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryDatabaseInitialStatusGatherer
import io.airbyte.integrations.destination.bigquery.write.BigqueryRawTableOperations
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigqueryBulkLoadConfiguration
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigqueryConfiguredForBulkLoad
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream
import java.io.InputStream
import java.nio.charset.StandardCharsets

private val logger = KotlinLogging.logger {}

@Factory
class BigqueryBeansFactory {
    @Singleton fun getConfig(config: DestinationConfiguration) = config as BigqueryConfiguration

    @Singleton
    @Requires(condition = BigqueryConfiguredForBulkLoad::class)
    fun getBulkLoadConfig(config: BigqueryConfiguration) = BigqueryBulkLoadConfiguration(config)

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
        streamStateStore: StreamStateStore<TypingDedupingExecutionConfig>,
    ): TypingDedupingWriter {
        val destinationHandler = BigQueryDatabaseHandler(bigquery, config.datasetLocation.region)
        return TypingDedupingWriter(
            names,
            BigqueryDatabaseInitialStatusGatherer(bigquery),
            destinationHandler,
            BigqueryRawTableOperations(bigquery),
            TypingDedupingFinalTableOperations(
                BigQuerySqlGenerator(config.projectId, config.datasetLocation.region),
                destinationHandler,
            ),
            disableTypeDedupe = config.disableTypingDeduping,
            streamStateStore,
        )
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
            .build()
            .service
    }
}
