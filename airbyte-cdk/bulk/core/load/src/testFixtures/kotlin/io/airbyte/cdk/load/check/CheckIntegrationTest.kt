/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.test.util.FakeDataDumper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.destination_process.TestDeploymentMode
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Path
import java.util.regex.Pattern
import kotlin.test.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

data class CheckTestConfig(val configPath: String, val deploymentMode: TestDeploymentMode)

open class CheckIntegrationTest<T : ConfigurationSpecification>(
    val configurationClass: Class<T>,
    val successConfigFilenames: List<CheckTestConfig>,
    val failConfigFilenamesAndFailureReasons: Map<CheckTestConfig, Pattern>,
) :
    IntegrationTest(
        FakeDataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
    ) {
    @Test
    open fun testSuccessConfigs() {
        for ((path, deploymentMode) in successConfigFilenames) {
            val fileContents = Files.readString(Path.of(path), StandardCharsets.UTF_8)
            val config = ValidatedJsonUtils.parseOne(configurationClass, fileContents)
            val process =
                destinationProcessFactory.createDestinationProcess(
                    "check",
                    config = config,
                    deploymentMode = deploymentMode,
                )
            process.run()
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
            val (path, deploymentMode) = checkTestConfig
            val fileContents = Files.readString(Path.of(path))
            val config = ValidatedJsonUtils.parseOne(configurationClass, fileContents)
            val process =
                destinationProcessFactory.createDestinationProcess(
                    "check",
                    config = config,
                    deploymentMode = deploymentMode,
                )
            process.run()
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
