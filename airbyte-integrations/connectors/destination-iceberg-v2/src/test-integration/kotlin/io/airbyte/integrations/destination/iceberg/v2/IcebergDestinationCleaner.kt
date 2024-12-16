package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.IntegrationTest.Companion.randomizedNamespaceDateFormatter
import io.airbyte.cdk.load.test.util.IntegrationTest.Companion.randomizedNamespaceRegex
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergUtil
import java.time.LocalDate
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.Namespace
import org.apache.iceberg.catalog.SupportsNamespaces

class IcebergDestinationCleaner(private val catalog: Catalog) : DestinationCleaner {
    constructor(configuration: IcebergV2Configuration) : this(
        IcebergUtil(SimpleTableIdGenerator()).let { icebergUtil ->
            val props = icebergUtil.toCatalogProperties(configuration)
            icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, props)
        }
    )

    override fun cleanup() {
        val cleanupCutoffDate = LocalDate.now().minusDays(15)
        val namespaces: List<Namespace> =
            (catalog as SupportsNamespaces)
                .listNamespaces()
                .filter {
                    val matchResult = randomizedNamespaceRegex.find(it.level(0))
                    if (matchResult == null) {
                        false
                    } else {
                        val namespaceCreationDate = LocalDate.parse(
                            matchResult.groupValues[1],
                            randomizedNamespaceDateFormatter
                        )
                        namespaceCreationDate.isBefore(cleanupCutoffDate)
                    }
                }
        namespaces.forEach { namespace ->
            catalog.listTables(namespace)
                .forEach { table -> catalog.dropTable(table, /* purge = */ true) }
            catalog.dropNamespace(namespace)
        }
    }
}
