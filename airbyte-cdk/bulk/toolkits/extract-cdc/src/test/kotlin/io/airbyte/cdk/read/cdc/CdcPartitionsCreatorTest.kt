/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.StringFieldType
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.Global
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
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

typealias CreatorPosition = Long

/** These unit tests play out the scenarios possible in [CdcPartitionsCreator.run]. */
@ExtendWith(MockKExtension::class)
class CdcPartitionsCreatorTest {

    @MockK lateinit var concurrencyResource: ConcurrencyResource

    @MockK(relaxUnitFun = true) lateinit var globalLockResource: CdcGlobalLockResource

    @MockK lateinit var outputConsumer: OutputConsumer

    @MockK lateinit var creatorOps: CdcPartitionsCreatorDebeziumOperations<CreatorPosition>

    @MockK lateinit var readerOps: CdcPartitionReaderDebeziumOperations<CreatorPosition>

    @MockK lateinit var stateQuerier: StateQuerier

    val stream =
        Stream(
            id = StreamIdentifier.from(StreamDescriptor().withName("test")),
            fields = listOf(Field("test", StringFieldType)),
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = null,
            configuredCursor = null,
        )

    val global = Global(listOf(stream))

    val upperBoundReference = AtomicReference<CreatorPosition>(null)

    val creator: CdcPartitionsCreator<CreatorPosition>
        get() =
            CdcPartitionsCreator(
                concurrencyResource,
                globalLockResource,
                stateQuerier,
                outputConsumer,
                creatorOps,
                readerOps,
                upperBoundReference,
                stateQuerier.current(global),
            )

    @Test
    fun testCreateWithSyntheticOffset() {
        every { stateQuerier.feeds } returns listOf(global, stream)
        val incumbentGlobalStateValue: OpaqueStateValue? = null
        every { stateQuerier.current(global) } returns incumbentGlobalStateValue
        val incumbentStreamStateValue: OpaqueStateValue? = null
        every { stateQuerier.current(stream) } returns incumbentStreamStateValue
        val syntheticOffset = DebeziumOffset(mapOf(Jsons.nullNode() to Jsons.nullNode()))
        every { creatorOps.position(syntheticOffset) } returns 123L
        val syntheticInput =
            DebeziumInput(
                properties = emptyMap(),
                state = DebeziumState(offset = syntheticOffset, schemaHistory = null),
                isSynthetic = true,
            )
        every { creatorOps.synthesize() } returns syntheticInput
        upperBoundReference.set(null)
        val readers: List<PartitionReader> = runBlocking { creator.run() }
        Assertions.assertEquals(1, readers.size)
        val reader = readers.first() as CdcPartitionReader<*>
        Assertions.assertEquals(123L, reader.upperBound)
        Assertions.assertEquals(syntheticInput, reader.input)
    }

    @Test
    fun testCreateWithDeserializedOffset() {
        every { stateQuerier.feeds } returns listOf(global, stream)
        val incumbentGlobalStateValue: OpaqueStateValue = Jsons.nullNode()
        every { stateQuerier.current(global) } returns incumbentGlobalStateValue
        val incumbentStreamStateValue: OpaqueStateValue = Jsons.nullNode()
        every { stateQuerier.current(stream) } returns incumbentStreamStateValue
        val incumbentOffset = DebeziumOffset(mapOf(Jsons.nullNode() to Jsons.nullNode()))
        every { creatorOps.position(incumbentOffset) } returns 123L
        val deserializedInput =
            DebeziumInput(
                properties = emptyMap(),
                state = DebeziumState(offset = incumbentOffset, schemaHistory = null),
                isSynthetic = false,
            )
        every { creatorOps.deserialize(incumbentGlobalStateValue, listOf(stream)) } returns
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
        every { stateQuerier.feeds } returns listOf(global, stream)
        val incumbentGlobalStateValue: OpaqueStateValue = Jsons.nullNode()
        every { stateQuerier.current(global) } returns incumbentGlobalStateValue
        val incumbentStreamStateValue: OpaqueStateValue = Jsons.nullNode()
        every { stateQuerier.current(stream) } returns incumbentStreamStateValue
        val incumbentOffset = DebeziumOffset(mapOf(Jsons.nullNode() to Jsons.nullNode()))
        every { creatorOps.position(incumbentOffset) } returns 123L
        val deserializedInput =
            DebeziumInput(
                properties = emptyMap(),
                state = DebeziumState(offset = incumbentOffset, schemaHistory = null),
                isSynthetic = false,
            )
        every { creatorOps.deserialize(incumbentGlobalStateValue, listOf(stream)) } returns
            deserializedInput
        upperBoundReference.set(1L)
        val readers: List<PartitionReader> = runBlocking { creator.run() }
        Assertions.assertEquals(emptyList<PartitionReader>(), readers)
    }

    @Test
    fun testCreateWithFailedValidation() {
        every { stateQuerier.feeds } returns listOf(global, stream)
        val incumbentGlobalStateValue: OpaqueStateValue = Jsons.nullNode()
        every { stateQuerier.current(global) } returns incumbentGlobalStateValue
        val incumbentStreamStateValue: OpaqueStateValue = Jsons.nullNode()
        every { stateQuerier.current(stream) } returns incumbentStreamStateValue
        val incumbentOffset = DebeziumOffset(mapOf(Jsons.nullNode() to Jsons.nullNode()))
        every { creatorOps.position(incumbentOffset) } returns 123L
        val syntheticOffset = DebeziumOffset(mapOf(Jsons.nullNode() to Jsons.nullNode()))
        val syntheticInput =
            DebeziumInput(
                properties = emptyMap(),
                state = DebeziumState(offset = syntheticOffset, schemaHistory = null),
                isSynthetic = true,
            )
        every { creatorOps.synthesize() } returns syntheticInput
        every { creatorOps.deserialize(incumbentGlobalStateValue, listOf(stream)) } throws
            ConfigErrorException("invalid state value")

        assertThrows(ConfigErrorException::class.java) { runBlocking { creator.run() } }
    }
}
