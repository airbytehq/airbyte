/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateEntry
import io.airbyte.cdk.load.dataflow.aggregate.AggregateStore
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
        val mockPartitionHistogram = mockk<PartitionHistogram>()
        val aggregateEntry =
            mockk<AggregateEntry> {
                every { value } returns mockAggregate
                every { partitionHistogram } returns mockPartitionHistogram
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
                    partitionHistogram = mockPartitionHistogram
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
        val mockPartitionHistogram1 = mockk<PartitionHistogram>()
        val aggregateEntry1 =
            mockk<AggregateEntry> {
                every { value } returns mockAggregate1
                every { partitionHistogram } returns mockPartitionHistogram1
            }

        val mockAggregate2 = mockk<Aggregate>()
        val mockPartitionHistogram2 = mockk<PartitionHistogram>()
        val aggregateEntry2 =
            mockk<AggregateEntry> {
                every { value } returns mockAggregate2
                every { partitionHistogram } returns mockPartitionHistogram2
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
                    partitionHistogram = mockPartitionHistogram1
                )
            )
        }
        coVerify(exactly = 1) {
            outputFlow.emit(
                DataFlowStageIO(
                    aggregate = mockAggregate2,
                    partitionHistogram = mockPartitionHistogram2
                )
            )
        }
    }
}
