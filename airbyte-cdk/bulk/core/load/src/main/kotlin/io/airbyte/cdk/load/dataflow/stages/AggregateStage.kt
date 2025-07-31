package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.Aggregate
import io.airbyte.cdk.load.dataflow.AggregateStore
import io.airbyte.cdk.load.dataflow.DataFlowStage
import io.airbyte.cdk.load.dataflow.DataFlowStageIO
import jakarta.inject.Named
import jakarta.inject.Singleton

@Named("aggregate")
@Singleton
class AggregateStage(
    val store: AggregateStore,
): DataFlowStage {
    override suspend fun apply(input: DataFlowStageIO): DataFlowStageIO {
        val key = input.raw!!.stream.mappedDescriptor

        val aggregateToFlush = if (!store.canAggregate(key)) {
            store.getAndRemoveBiggestAggregate()
        } else {
            null
        }

        val agg = store.getOrCreate(key)

        val result = agg.accept(input.munged!!)

        return when (result) {
            Aggregate.Status.COMPLETE -> input.apply { aggregate = store.remove(key) }
            Aggregate.Status.INCOMPLETE ->
                // This is working because we are assuming that the accept function doesn't return COMPLETE on the fist call.
                // It could be solved by having a list of aggregate or a transform operation.
                if (aggregateToFlush == null)
                    input.apply { skip = true }
                else
                    input.apply { aggregate = aggregateToFlush }
            }
    }
}
