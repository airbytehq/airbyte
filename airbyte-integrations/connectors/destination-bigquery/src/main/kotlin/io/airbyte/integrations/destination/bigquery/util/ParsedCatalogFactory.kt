package io.airbyte.integrations.destination.bigquery.util

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

// TODO this is... probably a temporary thing?
//   probably should replace it with better concepts in the bulk CDK
@Factory
class ParsedCatalogFactory(
    private val catalog: DestinationCatalog,
    private val config: BigqueryConfiguration,
    private val sqlGenerator: BigQuerySqlGenerator,
) {
    @Singleton
    fun make(): ParsedCatalog =
        CatalogParser(
                sqlGenerator,
                defaultNamespace = config.datasetId,
                rawNamespace = config.rawTableDataset,
            )
            .parseCatalog(catalog.asProtocolObject())
}
