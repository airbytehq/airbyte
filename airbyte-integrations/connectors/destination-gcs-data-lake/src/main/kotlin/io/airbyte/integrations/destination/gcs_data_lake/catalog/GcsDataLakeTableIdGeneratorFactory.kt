/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.micronaut.context.annotation.Factory
import javax.inject.Singleton

@Factory
class GcsDataLakeTableIdGeneratorFactory(
    private val gcsDataLakeConfiguration: GcsDataLakeConfiguration
) {
    @Singleton
    fun create(): TableIdGenerator = SimpleTableIdGenerator(gcsDataLakeConfiguration.databaseName)
}
