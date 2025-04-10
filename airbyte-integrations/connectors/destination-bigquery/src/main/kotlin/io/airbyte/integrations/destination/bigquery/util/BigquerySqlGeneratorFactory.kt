package io.airbyte.integrations.destination.bigquery.util

import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class BigquerySqlGeneratorFactory(private val config: BigqueryConfiguration) {
    @Singleton
    fun make(): BigQuerySqlGenerator =
        BigQuerySqlGenerator(config.projectId, config.datasetLocation.region)
}
