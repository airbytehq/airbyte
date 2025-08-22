/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.DataMunger
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.verify
import java.util.UUID
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class ParseStageTest {
    @MockK private lateinit var munger: DataMunger

    private lateinit var stage: ParseStage
    private lateinit var stream: DestinationStream
    private lateinit var rawRecord: DestinationRecordRaw

    @BeforeEach
    fun setup() {
        stage = ParseStage(munger)
        stream =
            DestinationStream(
                unmappedNamespace = "test-namespace",
                unmappedName = "test-stream",
                importType = Append,
                schema = io.airbyte.cdk.load.data.ObjectType(linkedMapOf()),
                generationId = 1L,
                minimumGenerationId = 1L,
                syncId = 1L,
                namespaceMapper = NamespaceMapper()
            )
        rawRecord =
            DestinationRecordRaw(
                stream = stream,
                rawData =
                    DestinationRecordJsonSource(
                        AirbyteMessage().withRecord(AirbyteRecordMessage().withEmittedAt(12345L))
                    ),
                serializedSizeBytes = 100,
                airbyteRawId = UUID.randomUUID(),
            )
    }

    @Test
    fun `given valid input, when apply is called, then it should munge the raw record and update the IO object`() =
        runTest {
            // Given
            val input =
                DataFlowStageIO(raw = rawRecord, partitionKey = PartitionKey("test-partition"))
            val transformedFields =
                mapOf("field1" to StringValue("value1"), "field2" to StringValue("42"))
            every { munger.transformForDest(rawRecord) } returns transformedFields

            // When
            val result = stage.apply(input)

            // Then
            assertSame(input, result, "The stage should return the same input object instance")
            assertNotNull(result.munged)

            val mungedRecord = result.munged!!
            assertEquals(transformedFields, mungedRecord.fields)
            assertEquals(PartitionKey("test-partition"), mungedRecord.partitionKey)
            assertEquals(100L, mungedRecord.sizeBytes)
            assertEquals(12345L, mungedRecord.emittedAtMs)

            verify(exactly = 1) { munger.transformForDest(rawRecord) }
        }

    @Test
    fun `given input with null raw record, when apply is called, then it should throw NullPointerException`() {
        // Given
        val input = DataFlowStageIO(raw = null, partitionKey = PartitionKey("test-partition"))

        // When & Then
        assertThrows<NullPointerException> { runBlocking { stage.apply(input) } }
    }

    @Test
    fun `given input with null partition key, when apply is called, then it should throw NullPointerException`() {
        // Given
        val input = DataFlowStageIO(raw = rawRecord, partitionKey = null)
        val transformedFields = mapOf("field1" to StringValue("value1"))
        every { munger.transformForDest(rawRecord) } returns transformedFields

        // When & Then
        assertThrows<NullPointerException> { runBlocking { stage.apply(input) } }
    }
}
