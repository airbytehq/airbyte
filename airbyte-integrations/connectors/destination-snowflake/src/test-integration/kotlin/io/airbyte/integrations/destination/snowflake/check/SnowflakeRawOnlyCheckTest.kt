/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.check

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.CONFIG_WITH_AUTH_STAGING
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.getConfig
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

class SnowflakeRawOnlyCheckTest :
    CheckIntegrationTest<SnowflakeSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(
                    configContents = getRawOnlyConfig(),
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

    companion object {
        fun getRawOnlyConfig(): String {
            val config = Jsons.readTree(getConfig(CONFIG_WITH_AUTH_STAGING)) as ObjectNode
            config.put("disable_type_dedupe", true)
            return Jsons.writeValueAsString(config)
        }
    }
}
