/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

/**
 * CHECK with a URL pasted into Host, the way users copy it from the Snowflake console. No Snowflake
 * account is involved. What the driver tolerates (`https://`, a trailing `/`, `:443`) is normalized
 * away and the driver is asked to connect; on Airbyte Cloud what it cannot handle (a path,
 * credentials, another port) is rejected before that, and outside Cloud the driver fails on its own
 * with a different message.
 */
class SnowflakeSourceCloudHostCheckTest {

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "https://app.snowflake.com/org/acct",
                "user@acct.snowflakecomputing.com",
                "acct.snowflakecomputing.com:8443",
            ],
    )
    fun testUnusableHostOnCloudIsRejectedBeforeConnecting(host: String) {
        val output: BufferingOutputConsumer =
            CliRunner.source(
                    "check",
                    config(host),
                    null,
                    null,
                    FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT,
                )
                .run()
        val status: AirbyteConnectionStatus = output.statuses().single()
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        Assertions.assertEquals(
            "Could not connect with provided configuration. Error: " +
                SnowflakeSourceMetadataQuerier.HOST_SYNTAX_MESSAGE,
            status.message,
        )
        val error: AirbyteErrorTraceMessage =
            output.traces().single { it.type == AirbyteTraceMessage.Type.ERROR }.error
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            error.failureType,
        )
        Assertions.assertEquals(SnowflakeSourceMetadataQuerier.HOST_SYNTAX_MESSAGE, error.message)
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "https://acct.snowflakecomputing.com",
                "acct.snowflakecomputing.com:443",
            ],
    )
    fun testTolerableHostOnCloudReachesTheDriver(host: String) {
        val output: BufferingOutputConsumer =
            CliRunner.source(
                    "check",
                    config(host),
                    null,
                    null,
                    FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT,
                )
                .run()
        assertFailedAtTheDriver(output)
    }

    @Test
    fun testUnusableHostOutsideCloudGetsTheDriverError() {
        val output: BufferingOutputConsumer =
            CliRunner.source("check", config("https://app.snowflake.com/org/acct")).run()
        assertFailedAtTheDriver(output)
    }

    /** Whatever the driver says about a host nothing answers for, it is not the host message. */
    private fun assertFailedAtTheDriver(output: BufferingOutputConsumer) {
        val status: AirbyteConnectionStatus = output.statuses().single()
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        Assertions.assertFalse(
            status.message.contains(SnowflakeSourceMetadataQuerier.HOST_SYNTAX_MESSAGE),
            status.message,
        )
    }

    companion object {
        fun config(host: String): SnowflakeSourceConfigurationSpecification =
            SnowflakeSourceConfigurationSpecification().apply {
                this.host = host
                role = "AIRBYTE_ROLE"
                warehouse = "AIRBYTE_WAREHOUSE"
                database = "AIRBYTE_DATABASE"
                // A token writes no key file to the working directory, unlike key pair auth.
                credentials =
                    ProgrammaticAccessTokenCredentialsSpecification(
                        programmaticAccessToken = "not-a-real-token",
                    )
            }
    }
}
