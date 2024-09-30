/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.write

import io.airbyte.cdk.command.Append
import io.airbyte.cdk.command.ConfigurationJsonObjectBase
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.message.DestinationRecord
import io.airbyte.cdk.message.StreamCheckpoint
import io.airbyte.cdk.test.util.DestinationCleaner
import io.airbyte.cdk.test.util.DestinationDataDumper
import io.airbyte.cdk.test.util.ExpectedRecordMapper
import io.airbyte.cdk.test.util.IntegrationTest
import io.airbyte.cdk.test.util.NameMapper
import io.airbyte.cdk.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.test.util.NoopNameMapper
import io.airbyte.cdk.test.util.OutputRecord
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

abstract class BasicFunctionalityIntegrationTest(
    val config: ConfigurationJsonObjectBase,
    dataDumper: DestinationDataDumper,
    destinationCleaner: DestinationCleaner,
    recordMangler: ExpectedRecordMapper = NoopExpectedRecordMapper,
    nameMapper: NameMapper = NoopNameMapper,
    /**
     * Whether to actually verify that the connector wrote data to the destination. This should only
     * ever be disabled for test destinations (dev-null, etc.).
     */
    val verifyDataWriting: Boolean = true,
) : IntegrationTest(dataDumper, destinationCleaner, recordMangler, nameMapper) {
    @Test
    open fun testCheck() {
        val process = destinationProcessFactory.createDestinationProcess("check", config = config)
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

    @Test
    open fun testBasicWrite() {
        val messages =
            runSync(
                config,
                DestinationStream(
                    DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                    Append,
                    ObjectTypeWithoutSchema,
                    generationId = 0,
                    minimumGenerationId = 0,
                    syncId = 42,
                ),
                listOf(
                    DestinationRecord(
                        namespace = randomizedNamespace,
                        name = "test_stream",
                        data = """{"id": 5678}""",
                        emittedAtMs = 1234,
                    ),
                    StreamCheckpoint(
                        streamName = "test_stream",
                        streamNamespace = randomizedNamespace,
                        blob = """{"foo": "bar"}""",
                        sourceRecordCount = 1,
                    )
                )
            )

        val stateMessages = messages.filter { it.type == AirbyteMessage.Type.STATE }
        assertAll(
            {
                assertEquals(
                    1,
                    stateMessages.size,
                    "Expected to receive exactly one state message, got ${stateMessages.size} ($stateMessages)"
                )
                assertEquals(
                    StreamCheckpoint(
                            streamName = "test_stream",
                            streamNamespace = randomizedNamespace,
                            blob = """{"foo": "bar"}""",
                            sourceRecordCount = 1,
                            destinationRecordCount = 1,
                        )
                        .asProtocolMessage(),
                    stateMessages.first()
                )
            },
            {
                if (verifyDataWriting) {
                    dumpAndDiffRecords(
                        listOf(
                            OutputRecord(
                                extractedAt = 1234,
                                generationId = 0,
                                data = mapOf("id" to 5678),
                                airbyteMeta = """{"changes": [], "sync_id": 42}"""
                            )
                        ),
                        "test_stream",
                        randomizedNamespace,
                        primaryKey = listOf(listOf("id")),
                        cursor = null,
                    )
                }
            },
        )
    }
}
