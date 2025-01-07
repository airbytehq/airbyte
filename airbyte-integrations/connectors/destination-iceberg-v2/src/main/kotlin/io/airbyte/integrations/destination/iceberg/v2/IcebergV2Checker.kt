/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergTableCleaner
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergUtil
import javax.inject.Singleton
import org.apache.iceberg.Schema
import org.apache.iceberg.types.Types

@Singleton
class IcebergV2Checker(
    private val icebergTableCleaner: IcebergTableCleaner,
    private val icebergUtil: IcebergUtil,
    private val tableIdGenerator: TableIdGenerator,
) : DestinationChecker<IcebergV2Configuration> {

    override fun check(config: IcebergV2Configuration) {
        catalogValidation(config)
    }
    private fun catalogValidation(config: IcebergV2Configuration) {
        val catalogProperties = icebergUtil.toCatalogProperties(config)
        val catalog = icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, catalogProperties)

        val testTableIdentifier = DestinationStream.Descriptor(TEST_NAMESPACE, TEST_TABLE)

        val testTableSchema =
            Schema(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.optional(2, "data", Types.StringType.get()),
            )
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
