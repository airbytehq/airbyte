/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.check

import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.CONFIG_WITH_AUTH_STAGING
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.CONFIG_WITH_AUTH_STAGING_IGNORE_CASING
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.getConfig
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

class SnowflakeCheckTest :
    CheckIntegrationTest<SnowflakeSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(
                    configContents = getConfig(CONFIG_WITH_AUTH_STAGING),
                    featureFlags = setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                ),
                CheckTestConfig(
                    configContents = getConfig(CONFIG_WITH_AUTH_STAGING_IGNORE_CASING),
                    featureFlags = setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                ),
            ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
    ) {
    @Test
    @Timeout(5, unit = TimeUnit.MINUTES)
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }
}
