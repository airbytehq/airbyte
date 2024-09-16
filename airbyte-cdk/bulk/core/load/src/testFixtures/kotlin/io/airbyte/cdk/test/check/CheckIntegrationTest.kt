/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.check

import io.airbyte.cdk.command.ConfigurationJsonObjectBase
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.test.util.FakeDataDumper
import io.airbyte.cdk.test.util.IntegrationTest
import io.airbyte.cdk.test.util.NoopDestinationCleaner
import io.airbyte.cdk.test.util.NoopExpectedRecordMapper
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

open class CheckIntegrationTest<T : ConfigurationJsonObjectBase>(
    val configurationClass: Class<T>,
    val successConfigFilenames: List<String>,
    val failConfigFilenamesAndFailureReasons: Map<String, Pattern>,
) :
    IntegrationTest(
        FakeDataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
    ) {
    @Test
    open fun testSuccessConfigs() {
        for (path in successConfigFilenames) {
            val fileContents = Files.readString(Path.of(path), StandardCharsets.UTF_8)
            val config = ValidatedJsonUtils.parseOne(configurationClass, fileContents)
            val process =
                destinationProcessFactory.createDestinationProcess("check", config = config)
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
                checkMessages.first().connectionStatus.status
            )
        }
    }

    @Test
    open fun testFailConfigs() {
        for ((path, failurePattern) in failConfigFilenamesAndFailureReasons) {
            val fileContents = Files.readString(Path.of(path))
            val config = ValidatedJsonUtils.parseOne(configurationClass, fileContents)
            val process =
                destinationProcessFactory.createDestinationProcess("check", config = config)
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
                        failurePattern.matcher(connectionStatus.message).matches(),
                        "Expected to match ${failurePattern.pattern()}, but got ${connectionStatus.message}"
                    )
                }
            )
        }
    }
}
