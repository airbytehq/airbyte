package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.aggregate.AggregateStore
import io.airbyte.cdk.load.dataflow.DataFlowStageIO
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.FlowCollector

typealias AggAndPublish = suspend FlowCollector<DataFlowStageIO>.(DataFlowStageIO) -> Unit

@Named("aggregate")
@Singleton
class AggregateStage(
    val store: AggregateStore,
): AggAndPublish {
    override suspend fun invoke(
        ouputFlow: FlowCollector<DataFlowStageIO>,
        input: DataFlowStageIO,
    ) {
        val key = input.raw!!.stream.mappedDescriptor
        val rec = input.munged!!

        store.acceptFor(key, rec)

        var next = store.removeNextComplete(rec.emittedAtMs)

        while (next != null) {
            ouputFlow.emit(DataFlowStageIO(aggregate = next))
            next = store.removeNextComplete(rec.emittedAtMs)
        }
    }
}
