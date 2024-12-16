/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.IntegrationTest.Companion.isNamespaceOld
import io.airbyte.cdk.load.test.util.IntegrationTest.Companion.randomizedNamespaceRegex
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergUtil
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.Namespace
import org.apache.iceberg.catalog.SupportsNamespaces

class IcebergDestinationCleaner(private val catalog: Catalog) : DestinationCleaner {
    constructor(
        configuration: IcebergV2Configuration
    ) : this(
        IcebergUtil(SimpleTableIdGenerator()).let { icebergUtil ->
            val props = icebergUtil.toCatalogProperties(configuration)
            icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, props)
        }
    )

    override fun cleanup() {
        val namespaces: List<Namespace> =
            (catalog as SupportsNamespaces).listNamespaces().filter {
                val namespace = it.level(0)
                randomizedNamespaceRegex.matches(namespace) && isNamespaceOld(namespace)
            }
        namespaces.forEach { namespace ->
            catalog.listTables(namespace).forEach { table ->
                catalog.dropTable(table, /* purge = */ true)
            }
            catalog.dropNamespace(namespace)
        }
    }
}
