/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.IntegrationTest.Companion.isNamespaceOld
import io.airbyte.cdk.load.test.util.IntegrationTest.Companion.randomizedNamespaceRegex
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableCleaner
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
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
        val tableCleaner = IcebergTableCleaner(IcebergUtil(SimpleTableIdGenerator()))

        runBlocking(Dispatchers.IO) {
            namespaces.forEach { namespace ->
                launch {
                    catalog.listTables(namespace).forEach { tableId ->
                        try {
                            val table = catalog.loadTable(tableId)
                            tableCleaner.clearTable(catalog, tableId, table.io(), table.location())
                        } catch (e: Exception) {
                            // catalog.loadTable will fail if the table has no files.
                            // In this case, we can just hard drop the table, because we know it has
                            // no corresponding files.
                            catalog.dropTable(tableId)
                        }
                    }
                    catalog.dropNamespace(namespace)
                }
            }
        }
    }
}
