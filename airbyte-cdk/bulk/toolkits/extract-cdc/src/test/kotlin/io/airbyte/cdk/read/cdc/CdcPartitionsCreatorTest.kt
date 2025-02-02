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
    val reset = AtomicReference<String?>(null)

    val creator: CdcPartitionsCreator<CreatorPosition>
        get() =
            CdcPartitionsCreator(
                concurrencyResource,
                globalFeedBootstrap,
                creatorOps,
                readerOps,
                lowerBoundReference,
                upperBoundReference,
                reset,
            )

    val syntheticOffset = DebeziumOffset(mapOf(Jsons.objectNode() to Jsons.objectNode()))
    val incumbentOffset = DebeziumOffset(mapOf(Jsons.objectNode() to Jsons.objectNode()))

    @BeforeEach
    fun setup() {
        every { globalFeedBootstrap.feed } returns global
        every { globalFeedBootstrap.feeds } returns listOf(global, stream)
        every { globalFeedBootstrap.streamRecordConsumers() } returns emptyMap()
        every { creatorOps.position(syntheticOffset) } returns 123L
        every { creatorOps.position(incumbentOffset) } returns 123L
        every { creatorOps.generateColdStartOffset() } returns syntheticOffset
        every { creatorOps.generateColdStartProperties() } returns emptyMap()
        every { creatorOps.generateWarmStartProperties(listOf(stream)) } returns emptyMap()
    }

    @Test
    fun testCreateWithSyntheticOffset() {
        every { globalFeedBootstrap.currentState } returns null
        every { globalFeedBootstrap.currentState(stream) } returns null
        val syntheticOffset = DebeziumOffset(mapOf(Jsons.nullNode() to Jsons.nullNode()))
        every { creatorOps.position(syntheticOffset) } returns 123L
        every { creatorOps.generateColdStartOffset() } returns syntheticOffset
        upperBoundReference.set(null)
        val readers: List<PartitionReader> = runBlocking { creator.run() }
        Assertions.assertEquals(1, readers.size)
        val reader = readers.first() as CdcPartitionReader<*>
        Assertions.assertEquals(123L, reader.upperBound)
        Assertions.assertEquals(syntheticOffset, reader.startingOffset)
    }

    @Test
    fun testCreateWithDeserializedOffset() {
        every { globalFeedBootstrap.currentState } returns Jsons.objectNode()
        every { globalFeedBootstrap.currentState(stream) } returns Jsons.objectNode()
        val deserializedState =
            ValidDebeziumWarmStartState(offset = incumbentOffset, schemaHistory = null)
        every { creatorOps.deserializeState(Jsons.objectNode()) } returns deserializedState
        upperBoundReference.set(1_000_000L)
        val readers: List<PartitionReader> = runBlocking { creator.run() }
        Assertions.assertEquals(1, readers.size)
        val reader = readers.first() as CdcPartitionReader<*>
        Assertions.assertEquals(1_000_000L, reader.upperBound)
        Assertions.assertEquals(deserializedState.offset, reader.startingOffset)
    }

    @Test
    fun testCreateNothing() {
        every { globalFeedBootstrap.currentState } returns Jsons.objectNode()
        every { globalFeedBootstrap.currentState(stream) } returns Jsons.objectNode()
        val deserializedState =
            ValidDebeziumWarmStartState(offset = incumbentOffset, schemaHistory = null)
        every { creatorOps.deserializeState(Jsons.objectNode()) } returns deserializedState
        upperBoundReference.set(1L)
        val readers: List<PartitionReader> = runBlocking { creator.run() }
        Assertions.assertEquals(emptyList<PartitionReader>(), readers)
    }

    @Test
    fun testCreateWithFailedValidation() {
        every { globalFeedBootstrap.currentState } returns Jsons.objectNode()
        every { globalFeedBootstrap.currentState(stream) } returns Jsons.objectNode()
        every { creatorOps.deserializeState(Jsons.objectNode()) } returns
            AbortDebeziumWarmStartState("boom")
        assertThrows(ConfigErrorException::class.java) { runBlocking { creator.run() } }
    }
}
