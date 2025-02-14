/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableCleaner
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.gcs_data_lake.io.GcsDataLakeUtil
import javax.inject.Singleton
import org.apache.iceberg.Schema
import org.apache.iceberg.types.Types

@Singleton
class GcsDataLakeChecker(
    private val icebergTableCleaner: IcebergTableCleaner,
    private val gcsDataLakeUtil: GcsDataLakeUtil,
    private val icebergUtil: IcebergUtil,
    private val tableIdGenerator: TableIdGenerator,
) : DestinationChecker<GcsDataLakeConfiguration> {

    override fun check(config: GcsDataLakeConfiguration) {
        catalogValidation(config)
    }
    private fun catalogValidation(config: GcsDataLakeConfiguration) {
        val catalogProperties = gcsDataLakeUtil.toCatalogProperties(config)
        val catalog = icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, catalogProperties)

        val testTableIdentifier = DestinationStream.Descriptor(TEST_NAMESPACE, TEST_TABLE)

        val testTableSchema =
            Schema(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.optional(2, "data", Types.StringType.get()),
            )
        gcsDataLakeUtil.createNamespaceWithGlueHandling(testTableIdentifier, catalog)
        val table =
            icebergUtil.createTable(
                testTableIdentifier,
                catalog,
                testTableSchema,
                catalogProperties,
            )

        icebergTableCleaner.clearTable(
            catalog,
            tableIdGenerator.toTableIdentifier(testTableIdentifier),
            table.io(),
            table.location()
        )
    }
}
