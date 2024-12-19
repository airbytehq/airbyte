/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.StringFieldType
import io.airbyte.cdk.discover.TestMetaFieldDecorator
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.StateQuerier
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertThrows
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

typealias CreatorPosition = Long

/** These unit tests play out the scenarios possible in [CdcPartitionsCreator.run]. */
@ExtendWith(MockKExtension::class)
class CdcPartitionsCreatorTest {

    @MockK lateinit var concurrencyResource: ConcurrencyResource

    @MockK lateinit var creatorOps: CdcPartitionsCreatorDebeziumOperations<CreatorPosition>

    @MockK lateinit var readerOps: CdcPartitionReaderDebeziumOperations<CreatorPosition>

    @MockK lateinit var stateQuerier: StateQuerier

    @MockK lateinit var globalFeedBootstrap: GlobalFeedBootstrap

    val stream =
        Stream(
            id = StreamIdentifier.from(StreamDescriptor().withName("test")),
            schema = setOf(Field("test", StringFieldType), TestMetaFieldDecorator.GlobalCursor),
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = null,
            configuredCursor = TestMetaFieldDecorator.GlobalCursor,
        )

    val global = Global(listOf(stream))

    val lowerBoundReference = AtomicReference<CreatorPosition>(null)
    val upperBoundReference = AtomicReference<CreatorPosition>(null)

    val creator: CdcPartitionsCreator<CreatorPosition>
        get() =
            CdcPartitionsCreator(
                concurrencyResource,
                globalFeedBootstrap,
                creatorOps,
                readerOps,
                lowerBoundReference,
                upperBoundReference,
            )

    val syntheticOffset = DebeziumOffset(mapOf(Jsons.objectNode() to Jsons.objectNode()))
    val incumbentOffset = DebeziumOffset(mapOf(Jsons.objectNode() to Jsons.objectNode()))
    val syntheticInput =
        DebeziumInput(
            properties = emptyMap(),
            state = DebeziumState(offset = syntheticOffset, schemaHistory = null),
            isSynthetic = true,
        )

    @BeforeEach
    fun setup() {
        every { globalFeedBootstrap.feed } returns global
        every { globalFeedBootstrap.stateQuerier } returns stateQuerier
        every { globalFeedBootstrap.streamRecordConsumers() } returns emptyMap()
        every { stateQuerier.feeds } returns listOf(global, stream)
        every { creatorOps.position(syntheticOffset) } returns 123L
        every { creatorOps.position(incumbentOffset) } returns 123L
        every { creatorOps.synthesize(listOf(stream)) } returns syntheticInput
    }

    @Test
    fun testCreateWithSyntheticOffset() {
        every { globalFeedBootstrap.currentState } returns null
        every { stateQuerier.current(stream) } returns null
        val syntheticOffset = DebeziumOffset(mapOf(Jsons.nullNode() to Jsons.nullNode()))
        every { creatorOps.position(syntheticOffset) } returns 123L
        val syntheticInput =
            DebeziumInput(
                properties = emptyMap(),
                state = DebeziumState(offset = syntheticOffset, schemaHistory = null),
                isSynthetic = true,
            )
        every { creatorOps.synthesize(listOf(stream)) } returns syntheticInput
        upperBoundReference.set(null)
        val readers: List<PartitionReader> = runBlocking { creator.run() }
        Assertions.assertEquals(1, readers.size)
        val reader = readers.first() as CdcPartitionReader<*>
        Assertions.assertEquals(123L, reader.upperBound)
        Assertions.assertEquals(syntheticInput, reader.input)
    }

    @Test
    fun testCreateWithDeserializedOffset() {
        every { globalFeedBootstrap.currentState } returns Jsons.objectNode()
        every { stateQuerier.current(stream) } returns Jsons.objectNode()
        val deserializedInput =
            DebeziumInput(
                properties = emptyMap(),
                state = DebeziumState(offset = incumbentOffset, schemaHistory = null),
                isSynthetic = false,
            )
        every { creatorOps.deserialize(Jsons.objectNode(), listOf(stream)) } returns
            deserializedInput
        upperBoundReference.set(1_000_000L)
        val readers: List<PartitionReader> = runBlocking { creator.run() }
        Assertions.assertEquals(1, readers.size)
        val reader = readers.first() as CdcPartitionReader<*>
        Assertions.assertEquals(1_000_000L, reader.upperBound)
        Assertions.assertEquals(deserializedInput, reader.input)
    }

    @Test
    fun testCreateNothing() {
        every { globalFeedBootstrap.currentState } returns Jsons.objectNode()
        every { stateQuerier.current(stream) } returns Jsons.objectNode()
        val deserializedInput =
            DebeziumInput(
                properties = emptyMap(),
                state = DebeziumState(offset = incumbentOffset, schemaHistory = null),
                isSynthetic = false,
            )
        every { creatorOps.deserialize(Jsons.objectNode(), listOf(stream)) } returns
            deserializedInput
        upperBoundReference.set(1L)
        val readers: List<PartitionReader> = runBlocking { creator.run() }
        Assertions.assertEquals(emptyList<PartitionReader>(), readers)
    }

    @Test
    fun testCreateWithFailedValidation() {
        every { globalFeedBootstrap.currentState } returns Jsons.objectNode()
        every { stateQuerier.current(stream) } returns Jsons.objectNode()
        every { creatorOps.deserialize(Jsons.objectNode(), listOf(stream)) } throws
            ConfigErrorException("invalid state value")
        assertThrows(ConfigErrorException::class.java) { runBlocking { creator.run() } }
    }
}
