/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

class GcsV2CheckTest :
    CheckIntegrationTest<GcsV2Specification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(
                    GcsV2TestUtils.getConfig(GcsV2TestUtils.AVRO_UNCOMPRESSED_CONFIG_PATH),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                ),
                CheckTestConfig(
                    GcsV2TestUtils.getConfig(GcsV2TestUtils.AVRO_SNAPPY_CONFIG_PATH),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                ),
                CheckTestConfig(
                    GcsV2TestUtils.getConfig(GcsV2TestUtils.JSONL_CONFIG_PATH),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                ),
            ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
        additionalMicronautEnvs = GcsV2Destination.additionalMicronautEnvs,
    ) {
    @Test
    @Timeout(5, unit = TimeUnit.MINUTES)
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }
}
