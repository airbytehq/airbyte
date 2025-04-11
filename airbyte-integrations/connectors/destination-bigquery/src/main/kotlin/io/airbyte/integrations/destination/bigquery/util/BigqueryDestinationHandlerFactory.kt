package io.airbyte.integrations.destination.bigquery.util

import com.google.cloud.bigquery.BigQuery
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class BigqueryDestinationHandlerFactory(
    private val bigquery: BigQuery,
    private val config: BigqueryConfiguration,
) {
    @Singleton
    fun make(): BigQueryDestinationHandler =
        BigQueryDestinationHandler(bigquery, config.datasetLocation.region)
}
