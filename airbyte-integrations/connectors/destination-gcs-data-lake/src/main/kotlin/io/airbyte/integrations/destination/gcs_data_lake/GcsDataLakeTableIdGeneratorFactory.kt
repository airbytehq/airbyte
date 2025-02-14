/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.iceberg.parquet.NessieCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.RestCatalogConfiguration
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.micronaut.context.annotation.Factory
import javax.inject.Singleton

@Factory
class GcsDataLakeTableIdGeneratorFactory(
    private val gcsDataLakeConfiguration: GcsDataLakeConfiguration
) {
    @Singleton
    fun create() =
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
            // TODO glue catalog config is currently a valid option here, which is why we need this
            // clause
            //   we should remove it from the base toolkit + move that into the s3-data-lake
            // connector
            else ->
                throw ConfigErrorException(
                    "Unsupported catalog type: ${gcsDataLakeConfiguration.icebergCatalogConfiguration.catalogConfiguration::class.java.name}"
                )
        }
}
