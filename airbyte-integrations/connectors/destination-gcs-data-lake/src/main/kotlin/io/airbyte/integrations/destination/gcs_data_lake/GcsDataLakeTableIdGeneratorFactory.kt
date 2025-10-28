/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.command.iceberg.parquet.NessieCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.PolarisCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.RestCatalogConfiguration
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.micronaut.context.annotation.Factory
import javax.inject.Singleton

@Factory
class TableIdGeneratorFactory(private val gcsDataLakeConfiguration: GcsDataLakeConfiguration) {
    @Singleton
    fun create(): TableIdGenerator =
        when (gcsDataLakeConfiguration.icebergCatalogConfiguration.catalogConfiguration) {
            is NessieCatalogConfiguration ->
                SimpleTableIdGenerator(
                    (gcsDataLakeConfiguration.icebergCatalogConfiguration.catalogConfiguration
                            as NessieCatalogConfiguration)
                        .namespace
                )
            is RestCatalogConfiguration ->
                SimpleTableIdGenerator(
                    (gcsDataLakeConfiguration.icebergCatalogConfiguration.catalogConfiguration
                            as RestCatalogConfiguration)
                        .namespace
                )
            is PolarisCatalogConfiguration ->
                SimpleTableIdGenerator(
                    (gcsDataLakeConfiguration.icebergCatalogConfiguration.catalogConfiguration
                            as PolarisCatalogConfiguration)
                        .namespace
                )
            else ->
                throw IllegalArgumentException(
                    "Unsupported catalog type: ${gcsDataLakeConfiguration.icebergCatalogConfiguration.catalogConfiguration::class.java.name}"
                )
        }
}
