/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.FakeConfigurationUpdater
import io.airbyte.cdk.load.test.util.FakeDataDumper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Path
import java.util.regex.Pattern
import kotlin.test.assertEquals
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

data class CheckTestConfig(val configPath: Path, val featureFlags: Set<FeatureFlag> = emptySet())

open class CheckIntegrationTest<T : ConfigurationSpecification>(
    val successConfigFilenames: List<CheckTestConfig>,
    val failConfigFilenamesAndFailureReasons: Map<CheckTestConfig, Pattern>,
    additionalMicronautEnvs: List<String> = emptyList(),
    configUpdater: ConfigurationUpdater = FakeConfigurationUpdater,
) :
    IntegrationTest(
        additionalMicronautEnvs = additionalMicronautEnvs,
        dataDumper = FakeDataDumper,
        destinationCleaner = NoopDestinationCleaner,
        recordMangler = NoopExpectedRecordMapper,
        configUpdater = configUpdater,
    ) {
    @Test
    open fun testSuccessConfigs() {
        for ((path, featureFlags) in successConfigFilenames) {
            val config = updateConfig(Files.readString(path, StandardCharsets.UTF_8))
            val process =
                destinationProcessFactory.createDestinationProcess(
                    "check",
                    configContents = config,
                    featureFlags = featureFlags.toTypedArray(),
                )
            runBlocking { process.run() }
            val messages = process.readMessages()
            val checkMessages = messages.filter { it.type == AirbyteMessage.Type.CONNECTION_STATUS }

            assertEquals(
                checkMessages.size,
                1,
                "Expected to receive exactly one connection status message, but got ${checkMessages.size}: $checkMessages"
            )
            assertEquals(
                AirbyteConnectionStatus.Status.SUCCEEDED,
                checkMessages.first().connectionStatus.status,
                "Expected check to be successful, but message was ${checkMessages.first().connectionStatus}"
            )
        }
    }

    @Test
    open fun testFailConfigs() {
        for ((checkTestConfig, failurePattern) in failConfigFilenamesAndFailureReasons) {
            val (path, featureFlags) = checkTestConfig
            val config = updateConfig(Files.readString(path))
            val process =
                destinationProcessFactory.createDestinationProcess(
                    "check",
                    configContents = config,
                    featureFlags = featureFlags.toTypedArray(),
                )
            runBlocking { process.run() }
            val messages = process.readMessages()
            val checkMessages = messages.filter { it.type == AirbyteMessage.Type.CONNECTION_STATUS }

            assertEquals(
                checkMessages.size,
                1,
                "Expected to receive exactly one connection status message, but got ${checkMessages.size}: $checkMessages"
            )

            val connectionStatus = checkMessages.first().connectionStatus
            assertAll(
                { assertEquals(AirbyteConnectionStatus.Status.FAILED, connectionStatus.status) },
                {
                    assertTrue(
                        failurePattern.matcher(connectionStatus.message).find(),
                        "Expected to match ${failurePattern.pattern()}, but got ${connectionStatus.message}"
                    )
                }
            )
        }
    }
}
