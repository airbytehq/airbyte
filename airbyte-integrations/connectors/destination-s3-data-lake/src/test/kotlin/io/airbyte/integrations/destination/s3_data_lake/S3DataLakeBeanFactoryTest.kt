/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.TouchedKeys
import io.airbyte.integrations.destination.s3_data_lake.spec.IcebergDeleteFileType
import io.airbyte.integrations.destination.s3_data_lake.spec.IcebergTableFormatVersion
import io.airbyte.integrations.destination.s3_data_lake.spec.S3BucketConfiguration
import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeConfiguration
import io.mockk.mockk
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource

internal class S3DataLakeBeanFactoryTest {
    private val beanFactory = S3DataLakeBeanFactory()

    @ParameterizedTest
    @EnumSource(
        value = IcebergDeleteFileType::class,
        names = ["AUTOMATIC", "POSITIONAL", "DELETION_VECTOR"],
    )
    fun `delete-resolving modes cap aggregate records at touched key limit`(
        deleteFileType: IcebergDeleteFileType,
    ) {
        val configuredMaxRecords = TouchedKeys.MAX_CURRENT_WRITES.toLong() + 100L

        assertThat(
                beanFactory
                    .aggregatePublishingConfig(configuration(deleteFileType, configuredMaxRecords))
                    .maxRecordsPerAgg,
            )
            .isEqualTo(TouchedKeys.MAX_CURRENT_WRITES.toLong())
    }

    @Test
    fun `equality mode keeps the configured aggregate record limit`() {
        val configuredMaxRecords = TouchedKeys.MAX_CURRENT_WRITES.toLong() + 100L

        assertThat(
                beanFactory
                    .aggregatePublishingConfig(
                        configuration(IcebergDeleteFileType.EQUALITY, configuredMaxRecords),
                    )
                    .maxRecordsPerAgg,
            )
            .isEqualTo(configuredMaxRecords)
    }

    @ParameterizedTest
    @EnumSource(IcebergDeleteFileType::class)
    fun `configured aggregate limit below touched key limit is preserved`(
        deleteFileType: IcebergDeleteFileType,
    ) {
        val configuredMaxRecords = TouchedKeys.MAX_CURRENT_WRITES.toLong() - 1L

        assertThat(
                beanFactory
                    .aggregatePublishingConfig(configuration(deleteFileType, configuredMaxRecords))
                    .maxRecordsPerAgg,
            )
            .isEqualTo(configuredMaxRecords)
    }

    private fun configuration(
        deleteFileType: IcebergDeleteFileType,
        configuredMaxRecords: Long,
    ) =
        S3DataLakeConfiguration(
            awsAccessKeyConfiguration = mockk<AWSAccessKeyConfiguration>(relaxed = true),
            s3BucketConfiguration = mockk<S3BucketConfiguration>(relaxed = true),
            icebergCatalogConfiguration = mockk<IcebergCatalogConfiguration>(relaxed = true),
            flushBatchSizeMb = null,
            maxRecordsPerFlush = configuredMaxRecords,
            tableFormatVersion =
                if (deleteFileType == IcebergDeleteFileType.DELETION_VECTOR) {
                    IcebergTableFormatVersion.V3
                } else {
                    IcebergTableFormatVersion.V2
                },
            icebergDeleteFileType = deleteFileType,
        )
}
