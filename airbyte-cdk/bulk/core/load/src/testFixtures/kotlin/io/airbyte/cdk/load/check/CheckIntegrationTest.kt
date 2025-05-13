/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.FakeConfigurationUpdater
import io.airbyte.cdk.load.test.util.FakeDataDumper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.destination_process.NonDockerizedDestinationFactory
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.util.regex.Pattern
import kotlin.test.assertEquals
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

data class CheckTestConfig(
    val configContents: String,
    val featureFlags: Set<FeatureFlag> = emptySet(),
    val name: String? = null,
)

abstract class CheckIntegrationTest<T : ConfigurationSpecification>(
    val successConfigFilenames: List<CheckTestConfig>,
    val failConfigFilenamesAndFailureReasons: Map<CheckTestConfig, Pattern>,
    additionalMicronautEnvs: List<String> = emptyList(),
    micronautProperties: Map<Property, String> = emptyMap(),
    configUpdater: ConfigurationUpdater = FakeConfigurationUpdater,
) :
    IntegrationTest(
        additionalMicronautEnvs = additionalMicronautEnvs,
        dataDumper = FakeDataDumper,
        destinationCleaner = NoopDestinationCleaner,
        recordMangler = NoopExpectedRecordMapper,
        configUpdater = configUpdater,
        micronautProperties = micronautProperties,
    ) {
    @BeforeEach
    fun setupProcessFactory() {
        if (destinationProcessFactory is NonDockerizedDestinationFactory) {
            destinationProcessFactory.injectInputStream = false
        }
    }

    @Test
    open fun testSuccessConfigs() {
        for (tc in successConfigFilenames) {
            val updatedConfig = updateConfig(tc.configContents)
            val process =
                destinationProcessFactory.createDestinationProcess(
                    "check",
                    configContents = updatedConfig,
                    featureFlags = tc.featureFlags.toTypedArray(),
                    micronautProperties = micronautProperties,
                )
            runBlocking { process.run() }
            val messages = process.readMessages()
            val checkMessages = messages.filter { it.type == AirbyteMessage.Type.CONNECTION_STATUS }
            val testName = tc.name ?: ""

            assertEquals(
                checkMessages.size,
                1,
                "$testName: Expected to receive exactly one connection status message, but got ${checkMessages.size}: $checkMessages"
            )
            assertEquals(
                AirbyteConnectionStatus.Status.SUCCEEDED,
                checkMessages.first().connectionStatus.status,
                "$testName: Expected check to be successful, but message was ${checkMessages.first().connectionStatus}"
            )
        }
    }

    @Test
    open fun testFailConfigs() {
        for ((checkTestConfig, failurePattern) in failConfigFilenamesAndFailureReasons) {
            val (configContents, featureFlags) = checkTestConfig
            val updatedConfig = updateConfig(configContents)
            val process =
                destinationProcessFactory.createDestinationProcess(
                    "check",
                    configContents = updatedConfig,
                    featureFlags = featureFlags.toTypedArray(),
                    micronautProperties = micronautProperties,
                )
            runBlocking { process.run() }
            val messages = process.readMessages()
            val checkMessages = messages.filter { it.type == AirbyteMessage.Type.CONNECTION_STATUS }
            val testName = checkTestConfig.name ?: ""

            assertEquals(
                checkMessages.size,
                1,
                "$testName: Expected to receive exactly one connection status message, but got ${checkMessages.size}: $checkMessages"
            )

            val connectionStatus = checkMessages.first().connectionStatus
            assertAll(
                {
                    assertEquals(
                        AirbyteConnectionStatus.Status.FAILED,
                        connectionStatus.status,
                        "$testName: expected check to fail but succeeded",
                    )
                },
                {
                    assertTrue(
                        failurePattern.matcher(connectionStatus.message).find(),
                        "$testName: Expected to match ${failurePattern.pattern()}, but got ${connectionStatus.message}"
                    )
                }
            )
        }
    }
}
