/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config

import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.dataflow.aggregate.AggregateStore
import io.airbyte.cdk.load.dataflow.aggregate.AggregateStoreFactory
import io.airbyte.cdk.load.dataflow.finalization.StreamCompletionTracker
import io.airbyte.cdk.load.dataflow.input.DataFlowPipelineInputFlow
import io.airbyte.cdk.load.dataflow.input.JsonDestinationMessageInputFlow
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStage
import io.airbyte.cdk.load.dataflow.state.StateHistogramStore
import io.airbyte.cdk.load.dataflow.state.StateKeyClient
import io.airbyte.cdk.load.dataflow.state.StateStore
import io.airbyte.cdk.load.dataflow.state.stats.CommittedStatsStore
import io.airbyte.cdk.load.dataflow.state.stats.EmittedStatsStore
import io.airbyte.cdk.load.file.ClientSocket
import io.airbyte.cdk.load.message.DestinationMessageFactory
import io.airbyte.cdk.load.message.ProtocolMessageDeserializer
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.unmockkAll
import io.mockk.verify
import java.io.ByteArrayInputStream
import kotlinx.coroutines.CoroutineDispatcher
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class InputBeanFactoryTest {

    @MockK private lateinit var deserializer: ProtocolMessageDeserializer

    @MockK private lateinit var destinationMessageFactory: DestinationMessageFactory

    @MockK private lateinit var stateStore: StateStore

    @MockK private lateinit var stateKeyClient: StateKeyClient

    @MockK private lateinit var completionTracker: StreamCompletionTracker

    @MockK private lateinit var parseStage: DataFlowStage

    @MockK private lateinit var flushStage: DataFlowStage

    @MockK private lateinit var stateStage: DataFlowStage

    @MockK private lateinit var aggregateStoreFactory: AggregateStoreFactory

    @MockK private lateinit var stateHistogramStore: StateHistogramStore

    @MockK private lateinit var emittedStatsStore: EmittedStatsStore

    @MockK private lateinit var committedStatsStore: CommittedStatsStore

    @MockK private lateinit var aggregationDispatcher: CoroutineDispatcher

    @MockK private lateinit var flushDispatcher: CoroutineDispatcher

    private var aggregatePublishingConfig = AggregatePublishingConfig()

    private lateinit var factory: InputBeanFactory

    @BeforeEach
    fun setup() {
        factory = InputBeanFactory()
    }

    @AfterEach
    fun tearDown() {
        unmockkAll()
    }

    @Test
    fun `sockets should create ClientSocket instances from socket paths`() {
        // Given
        val socketPaths = listOf("/tmp/socket1", "/tmp/socket2", "/tmp/socket3")
        val bufferSizeBytes = 8192
        val socketConnectionTimeoutMs = 5000L

        // When
        val result =
            factory.sockets(
                socketPaths = socketPaths,
                bufferSizeBytes = bufferSizeBytes,
                socketConnectionTimeoutMs = socketConnectionTimeoutMs
            )

        // Then
        assertEquals(3, result.size)
        assertEquals("/tmp/socket1", result[0].socketPath)
        assertEquals("/tmp/socket2", result[1].socketPath)
        assertEquals("/tmp/socket3", result[2].socketPath)
    }

    @Test
    fun `sockets should create single ClientSocket for single path`() {
        // Given
        val socketPaths = listOf("/tmp/single.socket")
        val bufferSizeBytes = 16384
        val socketConnectionTimeoutMs = 10000L

        // When
        val result =
            factory.sockets(
                socketPaths = socketPaths,
                bufferSizeBytes = bufferSizeBytes,
                socketConnectionTimeoutMs = socketConnectionTimeoutMs
            )

        // Then
        assertEquals(1, result.size)
        assertEquals("/tmp/single.socket", result[0].socketPath)
    }

    @Test
    fun `socketStreams should create input streams from ClientSocket list`() {
        // Given
        val socket1 = mockk<ClientSocket>()
        val socket2 = mockk<ClientSocket>()
        val socket3 = mockk<ClientSocket>()
        val sockets = listOf(socket1, socket2, socket3)

        val mockInputStream1 = ByteArrayInputStream("stream1".toByteArray())
        val mockInputStream2 = ByteArrayInputStream("stream2".toByteArray())
        val mockInputStream3 = ByteArrayInputStream("stream3".toByteArray())

        every { socket1.openInputStream() } returns mockInputStream1
        every { socket2.openInputStream() } returns mockInputStream2
        every { socket3.openInputStream() } returns mockInputStream3

        // When
        val result = factory.socketStreams(sockets)

        // Then
        assertEquals(3, result.size)
        assertEquals(mockInputStream1, result[0])
        assertEquals(mockInputStream2, result[1])
        assertEquals(mockInputStream3, result[2])

        verify(exactly = 1) { socket1.openInputStream() }
        verify(exactly = 1) { socket2.openInputStream() }
        verify(exactly = 1) { socket3.openInputStream() }
    }

    @Test
    fun `socketStreams should handle single socket`() {
        // Given
        val socket = mockk<ClientSocket>()
        val sockets = listOf(socket)
        val mockInputStream = ByteArrayInputStream("single stream".toByteArray())

        every { socket.openInputStream() } returns mockInputStream

        // When
        val result = factory.socketStreams(sockets)

        // Then
        assertEquals(1, result.size)
        assertEquals(mockInputStream, result[0])
        verify(exactly = 1) { socket.openInputStream() }
    }

    @Test
    fun `stdInStreams should return System in`() {
        // When
        val result = factory.stdInStreams()

        // Then
        assertEquals(1, result.size)
        assertEquals(System.`in`, result[0])
    }

    @Test
    fun `messageFlows should create DestinationMessageInputFlow for each input stream`() {
        // Given
        val inputStream1 = ByteArrayInputStream("stream1".toByteArray())
        val inputStream2 = ByteArrayInputStream("stream2".toByteArray())
        val inputStreams = ConnectorInputStreams(listOf(inputStream1, inputStream2))

        // When
        val result =
            factory.messageFlows(
                inputStreams,
                DataChannelFormat.JSONL,
                deserializer,
                destinationMessageFactory
            )

        // Then
        assertEquals(2, result.size)
        assertNotNull(result[0])
        assertNotNull(result[1])
    }

    @Test
    fun `inputFlows should create DataFlowPipelineInputFlow for each message flow`() {
        // Given
        val messageFlow1 = mockk<JsonDestinationMessageInputFlow>()
        val messageFlow2 = mockk<JsonDestinationMessageInputFlow>()
        val messageFlows = listOf(messageFlow1, messageFlow2)

        // When
        val result =
            factory.inputFlows(
                messageFlows = messageFlows,
                stateStore = stateStore,
                stateKeyClient = stateKeyClient,
                completionTracker = completionTracker,
                statsStore = emittedStatsStore,
            )

        // Then
        assertEquals(2, result.size)
        assertNotNull(result[0])
        assertNotNull(result[1])
    }

    @Test
    fun `pipes should create DataFlowPipeline for each input flow`() {
        every { aggregateStoreFactory.make() } returns mockk()

        // Given
        val inputFlow1 = mockk<DataFlowPipelineInputFlow>()
        val inputFlow2 = mockk<DataFlowPipelineInputFlow>()
        val inputFlows = listOf(inputFlow1, inputFlow2)

        // When
        val result =
            factory.pipes(
                inputFlows = inputFlows,
                parse = parseStage,
                flush = flushStage,
                state = stateStage,
                aggregateStoreFactory = aggregateStoreFactory,
                stateHistogramStore = stateHistogramStore,
                statsStore = committedStatsStore,
                aggregatePublishingConfig = aggregatePublishingConfig,
                aggregationDispatcher = aggregationDispatcher,
                flushDispatcher = flushDispatcher,
            )

        // Then
        assertEquals(2, result.size)
        assertNotNull(result[0])
        assertNotNull(result[1])
    }

    @Test
    fun `pipes should create different aggregate store for each pipeline`() {
        // Given
        val inputFlow1 = mockk<DataFlowPipelineInputFlow>()
        val inputFlow2 = mockk<DataFlowPipelineInputFlow>()
        val inputFlow3 = mockk<DataFlowPipelineInputFlow>()
        val inputFlows = listOf(inputFlow1, inputFlow2, inputFlow3)

        val aggregateStore1 = mockk<AggregateStore>(relaxed = true)
        val aggregateStore2 = mockk<AggregateStore>(relaxed = true)
        val aggregateStore3 = mockk<AggregateStore>(relaxed = true)

        // Mock the factory to return different instances
        every { aggregateStoreFactory.make() } returnsMany
            listOf(aggregateStore1, aggregateStore2, aggregateStore3)

        // When
        val result =
            factory.pipes(
                inputFlows = inputFlows,
                parse = parseStage,
                flush = flushStage,
                state = stateStage,
                aggregateStoreFactory = aggregateStoreFactory,
                stateHistogramStore = stateHistogramStore,
                statsStore = committedStatsStore,
                aggregatePublishingConfig = aggregatePublishingConfig,
                aggregationDispatcher = aggregationDispatcher,
                flushDispatcher = flushDispatcher,
            )

        // Then
        assertEquals(3, result.size)

        // Verify that the factory was called 3 times to create 3 different stores
        verify(exactly = 3) { aggregateStoreFactory.make() }

        // Each pipeline should have received a different aggregate store
        // We can't directly verify which store went to which pipeline without accessing internals,
        // but we verified that 3 different stores were created via the factory
    }

    @Test
    fun `integration test - complete flow from socket paths to pipelines`() {
        // Given
        val mockInputStream1 = ByteArrayInputStream("stream1".toByteArray())
        val mockInputStream2 = ByteArrayInputStream("stream2".toByteArray())

        every { aggregateStoreFactory.make() } returns mockk()

        val inputStreams = ConnectorInputStreams(listOf(mockInputStream1, mockInputStream2))

        val messageFlows =
            factory.messageFlows(
                inputStreams,
                DataChannelFormat.JSONL,
                deserializer,
                destinationMessageFactory
            )

        val inputFlows =
            factory.inputFlows(
                messageFlows = messageFlows,
                stateStore = stateStore,
                stateKeyClient = stateKeyClient,
                completionTracker = completionTracker,
                statsStore = emittedStatsStore,
            )

        val pipes =
            factory.pipes(
                inputFlows = inputFlows,
                parse = parseStage,
                flush = flushStage,
                state = stateStage,
                aggregateStoreFactory = aggregateStoreFactory,
                stateHistogramStore = stateHistogramStore,
                statsStore = committedStatsStore,
                aggregatePublishingConfig = aggregatePublishingConfig,
                aggregationDispatcher = aggregationDispatcher,
                flushDispatcher = flushDispatcher,
            )

        // Then
        assertEquals(2, inputStreams.size)
        assertEquals(2, messageFlows.size)
        assertEquals(2, inputFlows.size)
        assertEquals(2, pipes.size)
    }
}
