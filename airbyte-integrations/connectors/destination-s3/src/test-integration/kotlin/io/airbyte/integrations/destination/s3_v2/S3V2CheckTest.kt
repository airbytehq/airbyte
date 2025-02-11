/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.cdk.load.command.aws.asMicronautProperties
import java.nio.file.Path
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

class S3V2CheckTest :
    CheckIntegrationTest<S3V2Specification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(
                    Path.of(S3V2TestUtils.JSON_UNCOMPRESSED_CONFIG_PATH),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT)
                ),
                //                Uncomment when staging is re-enabled.
                //                CheckTestConfig(
                //                    Path.of(S3V2TestUtils.JSON_STAGING_CONFIG_PATH),
                //                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                //                ),
                CheckTestConfig(
                    Path.of(S3V2TestUtils.JSON_GZIP_CONFIG_PATH),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                ),
                CheckTestConfig(
                    Path.of(S3V2TestUtils.CSV_UNCOMPRESSED_CONFIG_PATH),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                ),
                CheckTestConfig(
                    Path.of(S3V2TestUtils.CSV_GZIP_CONFIG_PATH),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                ),
                CheckTestConfig(
                    Path.of(S3V2TestUtils.ENDPOINT_EMPTY_URL_CONFIG_PATH),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                )
            ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
        additionalMicronautEnvs = S3V2Destination.additionalMicronautEnvs,
        micronautProperties = S3V2TestUtils.assumeRoleCredentials.asMicronautProperties(),
    ) {
    @Test
    @Timeout(5, unit = TimeUnit.MINUTES)
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }
}
