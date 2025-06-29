/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.data.icerberg.parquet.IcebergDestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationCleaner

object S3DataLakeCleaner : DestinationCleaner {
    private val actualCleaner =
        IcebergDestinationCleaner(
                S3DataLakeTestUtil.getCatalog(
                    S3DataLakeTestUtil.parseConfig(S3DataLakeTestUtil.GLUE_CONFIG_PATH),
                    S3DataLakeTestUtil.getAwsAssumeRoleCredentials(),
                ),
            )
            .compose(
                IcebergDestinationCleaner(
                    S3DataLakeTestUtil.getCatalog(
                        S3DataLakeTestUtil.parseConfig(
                            S3DataLakeTestUtil.GLUE_ASSUME_ROLE_CONFIG_PATH
                        ),
                        S3DataLakeTestUtil.getAwsAssumeRoleCredentials(),
                    ),
                ),
            )

    override fun cleanup() {
        actualCleaner.cleanup()
    }
}
