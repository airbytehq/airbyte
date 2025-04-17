/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import com.google.cloud.bigquery.BigQuery
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.TableNames
import io.airbyte.cdk.load.orchestration.legacy_typing_deduping.TypingDedupingFinalTableOperations
import io.airbyte.cdk.load.orchestration.legacy_typing_deduping.TypingDedupingWriter
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryDestinationInitialStatusGatherer
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class BigqueryWriterFactory(
    private val bigquery: BigQuery,
    private val config: BigqueryConfiguration,
    private val names: Map<DestinationStream, Pair<TableNames, ColumnNameMapping>>,
) {
    @Singleton
    fun make(): TypingDedupingWriter {
        val destinationHandler = BigQueryDestinationHandler(bigquery, config.datasetLocation.region)
        return TypingDedupingWriter(
            names,
            BigqueryDestinationInitialStatusGatherer(bigquery),
            destinationHandler,
            BigqueryRawTableOperations(bigquery),
            TypingDedupingFinalTableOperations(
                BigQuerySqlGenerator(config.projectId, config.datasetLocation.region),
                destinationHandler,
            ),
            disableTypeDedupe = config.disableTypingDeduping,
        )
    }
}
