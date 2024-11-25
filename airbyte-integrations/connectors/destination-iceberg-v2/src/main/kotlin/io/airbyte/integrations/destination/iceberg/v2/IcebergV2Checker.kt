/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergTableCleaner
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergUtil
import io.airbyte.integrations.destination.iceberg.v2.io.toIcebergTableIdentifier
import io.github.oshai.kotlinlogging.KotlinLogging
import javax.inject.Singleton
import org.apache.iceberg.Schema
import org.apache.iceberg.types.Types

@Singleton
class IcebergV2Checker(
    private val icebergTableCleaner: IcebergTableCleaner,
    private val icebergUtil: IcebergUtil
) : DestinationChecker<IcebergV2Configuration> {
    private val log = KotlinLogging.logger {}
    override fun check(config: IcebergV2Configuration) {
        catalogValidation(config)
    }
    private fun catalogValidation(config: IcebergV2Configuration) {
        val catalogProperties = icebergUtil.toCatalogProperties(config)
        log.info { "PROPERTIES_PROPERTIES" }
        catalogProperties.forEach { (key, value) -> log.info { "$key: $value" } }

        val catalog = icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, catalogProperties)

        log.info { "CATALOG CREATED" }
        val testTableIdentifier =
            DestinationStream.Descriptor("airbyte_test_namespace", "airbyte_test_table")

        val testTableSchema =
            Schema(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.optional(2, "data", Types.StringType.get()),
            )
        log.info { "CREATING TABLE" }
        val table =
            icebergUtil.createTable(
                testTableIdentifier,
                catalog,
                testTableSchema,
                catalogProperties,
            )

        log.info { "TABLE CREATED" }

        log.info { "CLEARNING TABLE" }

        icebergTableCleaner.clearTable(
            catalog,
            testTableIdentifier.toIcebergTableIdentifier(),
            table.io(),
            table.location()
        )

        log.info { "TABLE CLEARED" }
    }
}
