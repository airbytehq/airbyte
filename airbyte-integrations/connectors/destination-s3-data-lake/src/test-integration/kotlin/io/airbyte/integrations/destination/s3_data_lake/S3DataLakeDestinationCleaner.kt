/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.IntegrationTest.Companion.isNamespaceOld
import io.airbyte.cdk.load.test.util.IntegrationTest.Companion.randomizedNamespaceRegex
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeTableCleaner
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeUtil
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.Namespace
import org.apache.iceberg.catalog.SupportsNamespaces

class S3DataLakeDestinationCleaner(private val catalog: Catalog) : DestinationCleaner {
    override fun cleanup() {
        val namespaces: List<Namespace> =
            (catalog as SupportsNamespaces).listNamespaces().filter {
                val namespace = it.level(0)
                randomizedNamespaceRegex.matches(namespace) && isNamespaceOld(namespace)
            }

        // we're passing explicit TableIdentifier to clearTable, so just use SimpleTableIdGenerator
        val tableCleaner = S3DataLakeTableCleaner(S3DataLakeUtil(SimpleTableIdGenerator("")))

        namespaces.forEach { namespace ->
            catalog.listTables(namespace).forEach { tableId ->
                val table = catalog.loadTable(tableId)
                tableCleaner.clearTable(catalog, tableId, table.io(), table.location())
            }
            catalog.dropNamespace(namespace)
        }
    }
}
