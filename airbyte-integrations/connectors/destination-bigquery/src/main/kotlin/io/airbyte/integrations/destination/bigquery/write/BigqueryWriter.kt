/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import com.google.cloud.bigquery.BigQuery
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingExecutionConfig
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingFinalTableOperations
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingWriter
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDatabaseHandler
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryDatabaseInitialStatusGatherer
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class BigqueryWriterFactory(
    private val bigquery: BigQuery,
    private val config: BigqueryConfiguration,
    private val names: TableCatalog,
    private val streamStateStore: StreamStateStore<TypingDedupingExecutionConfig>,
) {
    @Singleton
    fun make(): TypingDedupingWriter {
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
            streamStateStore
        )
    }
}
