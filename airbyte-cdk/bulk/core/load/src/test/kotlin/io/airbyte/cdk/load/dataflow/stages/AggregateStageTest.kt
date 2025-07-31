package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.Aggregate
import io.airbyte.cdk.load.dataflow.AggregateStore
import io.airbyte.cdk.load.dataflow.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class AggregateStageTest {

    private val store: AggregateStore = mockk()
    private val stage = AggregateStage(store)

    @Test
    fun `test aggregation complete`() = runTest {
        val streamDescriptor = DestinationStream.Descriptor("test_namespace", "test_name")
        val aggregate = mockk<Aggregate>()
        val recordDto = mockk<RecordDTO>()
        val input = DataFlowStageIO(
            raw = mockk {
                every { stream } returns mockk {
                    every { mappedDescriptor } returns streamDescriptor
                }
            },
            munged = recordDto,
        )

        every { store.canAggregate(streamDescriptor) } returns true
        every { store.getOrCreate(streamDescriptor) } returns aggregate
        every { aggregate.accept(recordDto) } returns Aggregate.Status.COMPLETE
        every { store.remove(streamDescriptor) } returns aggregate

        val result = stage.apply(input)

        assertEquals(aggregate, result.aggregate)
        verify { store.remove(streamDescriptor) }
    }

    @Test
    fun `test aggregation incomplete`() = runTest {
        val streamDescriptor = DestinationStream.Descriptor("test_namespace", "test_name")
        val aggregate = mockk<Aggregate>()
        val recordDto = mockk<RecordDTO>()
        val input = DataFlowStageIO(
            raw = mockk {
                every { stream } returns mockk {
                    every { mappedDescriptor } returns streamDescriptor
                }
            },
            munged = recordDto,
        )

        every { store.canAggregate(streamDescriptor) } returns true
        every { store.getOrCreate(streamDescriptor) } returns aggregate
        every { aggregate.accept(recordDto) } returns Aggregate.Status.INCOMPLETE

        val result = stage.apply(input)

        assertTrue(result.skip)
        assertNull(result.aggregate)
    }

    @Test
    fun `test aggregation with flush`() = runTest {
        val streamDescriptor = DestinationStream.Descriptor("test_namespace", "test_name")
        val aggregateToFlush = mockk<Aggregate>()
        val aggregate = mockk<Aggregate>()
        val recordDto = mockk<RecordDTO>()
        val input = DataFlowStageIO(
            raw = mockk {
                every { stream } returns mockk {
                    every { mappedDescriptor } returns streamDescriptor
                }
            },
            munged = recordDto,
        )

        every { store.canAggregate(streamDescriptor) } returns false
        every { store.getAndRemoveBiggestAggregate() } returns aggregateToFlush
        every { store.getOrCreate(streamDescriptor) } returns aggregate
        every { aggregate.accept(recordDto) } returns Aggregate.Status.INCOMPLETE

        val result = stage.apply(input)

        assertEquals(aggregateToFlush, result.aggregate)
    }
}
