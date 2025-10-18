/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateEntry
import io.airbyte.cdk.load.dataflow.aggregate.AggregateStore
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.flow.FlowCollector
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class AggregateStageTest {

    private val store: AggregateStore = mockk(relaxed = true)
    private val stage = AggregateStage(store)

    @Test
    fun `test aggregation`() = runTest {
        val streamDescriptor = DestinationStream.Descriptor("test_namespace", "test_name")
        val emittedAtMs = 1L
        val partitionKey = PartitionKey("partition_id_1")
        val recordDto =
            RecordDTO(
                fields = emptyMap(),
                partitionKey = partitionKey,
                sizeBytes = 100L,
                emittedAtMs = emittedAtMs
            )

        val streamMock =
            mockk<DestinationStream> { every { mappedDescriptor } returns streamDescriptor }
        val rawMock = mockk<DestinationRecordRaw> { every { stream } returns streamMock }
        val input = DataFlowStageIO(raw = rawMock, munged = recordDto)

        val mockAggregate = mockk<Aggregate>()
        val mockCountsHistogram = mockk<PartitionHistogram>()
        val mockBytesHistogram = mockk<PartitionHistogram>()
        val aggregateEntry =
            mockk<AggregateEntry> {
                every { key } returns streamDescriptor
                every { value } returns mockAggregate
                every { partitionCountsHistogram } returns mockCountsHistogram
                every { partitionBytesHistogram } returns mockBytesHistogram
            }
        coEvery { store.acceptFor(streamDescriptor, recordDto) } returns Unit
        coEvery { store.removeNextComplete(emittedAtMs) } returns aggregateEntry andThen null

        val outputFlow = mockk<FlowCollector<DataFlowStageIO>>(relaxed = true)

        stage.apply(input, outputFlow)

        coVerify { store.acceptFor(streamDescriptor, recordDto) }
        coVerify { store.removeNextComplete(emittedAtMs) }
        coVerify {
            outputFlow.emit(
                DataFlowStageIO(
                    aggregate = mockAggregate,
                    partitionCountsHistogram = mockCountsHistogram,
                    partitionBytesHistogram = mockBytesHistogram,
                    mappedDesc = streamDescriptor,
                )
            )
        }
    }

    @Test
    fun `should not emit if no complete aggregate is ready`() = runTest {
        val streamDescriptor = DestinationStream.Descriptor("test_namespace", "test_name")
        val emittedAtMs = 1L
        val partitionKey = PartitionKey("partition_id_1")
        val recordDto =
            RecordDTO(
                fields = emptyMap(),
                partitionKey = partitionKey,
                sizeBytes = 100L,
                emittedAtMs = emittedAtMs
            )

        val streamMock =
            mockk<DestinationStream> { every { mappedDescriptor } returns streamDescriptor }
        val rawMock = mockk<DestinationRecordRaw> { every { stream } returns streamMock }
        val input = DataFlowStageIO(raw = rawMock, munged = recordDto)

        coEvery { store.acceptFor(streamDescriptor, recordDto) } returns Unit
        coEvery { store.removeNextComplete(emittedAtMs) } returns null // No aggregate ready

        val outputFlow = mockk<FlowCollector<DataFlowStageIO>>(relaxed = true)

        stage.apply(input, outputFlow)

        coVerify { store.acceptFor(streamDescriptor, recordDto) }
        coVerify { store.removeNextComplete(emittedAtMs) }
        coVerify(exactly = 0) { outputFlow.emit(any()) } // Verify no emission
    }

    @Test
    fun `should emit multiple times if multiple complete aggregates are ready`() = runTest {
        val streamDescriptor = DestinationStream.Descriptor("test_namespace", "test_name")
        val emittedAtMs = 1L
        val partitionKey = PartitionKey("partition_id_1")
        val recordDto =
            RecordDTO(
                fields = emptyMap(),
                partitionKey = partitionKey,
                sizeBytes = 100L,
                emittedAtMs = emittedAtMs
            )

        val streamMock =
            mockk<DestinationStream> { every { mappedDescriptor } returns streamDescriptor }
        val rawMock = mockk<DestinationRecordRaw> { every { stream } returns streamMock }
        val input = DataFlowStageIO(raw = rawMock, munged = recordDto)

        val mockAggregate1 = mockk<Aggregate>()
        val mockCounts1 = mockk<PartitionHistogram>()
        val mockBytes1 = mockk<PartitionHistogram>()
        val aggregateEntry1 =
            mockk<AggregateEntry> {
                every { key } returns streamDescriptor
                every { value } returns mockAggregate1
                every { partitionCountsHistogram } returns mockCounts1
                every { partitionBytesHistogram } returns mockBytes1
            }

        val mockAggregate2 = mockk<Aggregate>()
        val mockCounts2 = mockk<PartitionHistogram>()
        val mockBytes2 = mockk<PartitionHistogram>()
        val aggregateEntry2 =
            mockk<AggregateEntry> {
                every { key } returns streamDescriptor
                every { value } returns mockAggregate2
                every { partitionCountsHistogram } returns mockCounts2
                every { partitionBytesHistogram } returns mockBytes2
            }

        coEvery { store.acceptFor(streamDescriptor, recordDto) } returns Unit
        coEvery { store.removeNextComplete(emittedAtMs) } returns
            aggregateEntry1 andThen
            aggregateEntry2 andThen
            null

        val outputFlow = mockk<FlowCollector<DataFlowStageIO>>(relaxed = true)

        stage.apply(input, outputFlow)

        coVerify { store.acceptFor(streamDescriptor, recordDto) }
        coVerify { store.removeNextComplete(emittedAtMs) }
        coVerify(exactly = 1) {
            outputFlow.emit(
                DataFlowStageIO(
                    aggregate = mockAggregate1,
                    partitionCountsHistogram = mockCounts1,
                    partitionBytesHistogram = mockBytes1,
                    mappedDesc = streamDescriptor,
                )
            )
        }
        coVerify(exactly = 1) {
            outputFlow.emit(
                DataFlowStageIO(
                    aggregate = mockAggregate2,
                    partitionCountsHistogram = mockCounts2,
                    partitionBytesHistogram = mockBytes2,
                    mappedDesc = streamDescriptor,
                )
            )
        }
    }
}
