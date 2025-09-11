package io.airbyte.integrations.destination.snowflake.check

import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.cdk.load.command.EnvVarConstants.AIRBYTE_EDITION
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.getConfig
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

class SnowflakeCheckTest :
    CheckIntegrationTest<SnowflakeSpecification>(
        successConfigFilenames =
            listOf(
                //        CheckTestConfig(
                //            configContents =
                // getConfig(SnowflakeTestUtils.KEYPAIR_AUTH_CONFIG_PATH),
                //            featureFlags = setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                //        ),
                CheckTestConfig(
                    configContents = getConfig(SnowflakeTestUtils.USERNAME_AUTH_CONFIG_PATH),
                    featureFlags = setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                ),
            ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
        additionalMicronautEnvs = emptyList(),
        micronautProperties = mapOf(AIRBYTE_EDITION to "CLOUD")
    ) {
    @Test
    @Timeout(5, unit = TimeUnit.MINUTES)
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }
}
