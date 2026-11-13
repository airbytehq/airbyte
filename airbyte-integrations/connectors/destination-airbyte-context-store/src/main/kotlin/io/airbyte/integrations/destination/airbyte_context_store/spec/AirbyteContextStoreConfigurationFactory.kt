/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.airbyte_context_store.spec

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogSpecification
import io.airbyte.integrations.destination.s3_data_lake.spec.S3BucketRegion
import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeConfiguration
import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeConfigurationFactory
import io.micronaut.context.annotation.Replaces
import jakarta.inject.Singleton

/**
 * Builds the S3 Data Lake configuration that backs the context store. The storage, catalog and
 * credential values are supplied by Airbyte at runtime rather than by the customer, so a missing
 * value is a platform error and not something the customer can fix.
 */
@Singleton
@Replaces(S3DataLakeConfigurationFactory::class)
class AirbyteContextStoreConfigurationFactory :
    DestinationConfigurationFactory<AirbyteContextStoreSpecification, S3DataLakeConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: AirbyteContextStoreSpecification
    ): S3DataLakeConfiguration {
        if (!pojo.acknowledgeManagedStorage) {
            throw ConfigErrorException("Managed storage acknowledgement is not accepted.")
        }
        if (
            pojo.s3BucketName.isBlank() ||
                pojo.warehouseLocation.isBlank() ||
                pojo.mainBranchName.isBlank() ||
                pojo.s3BucketRegion == S3BucketRegion.NO_REGION
        ) {
            throw SystemErrorException("Managed storage configuration is missing.")
        }

        val catalog = pojo.catalogType
        if (catalog !is GlueCatalogSpecification) {
            throw SystemErrorException("Managed catalog configuration is not a Glue catalog.")
        }
        if (catalog.glueId.isBlank() || catalog.databaseName.isBlank()) {
            throw SystemErrorException("Managed catalog configuration is missing.")
        }

        return S3DataLakeConfiguration(
            awsAccessKeyConfiguration = pojo.toAWSAccessKeyConfiguration(),
            s3BucketConfiguration = pojo.toS3BucketConfiguration(),
            icebergCatalogConfiguration = pojo.toIcebergCatalogConfiguration(),
            flushBatchSizeMb = pojo.flushBatchSizeMb,
        )
    }
}
