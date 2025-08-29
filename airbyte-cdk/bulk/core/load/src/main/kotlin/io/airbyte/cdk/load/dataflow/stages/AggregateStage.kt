/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.aggregate.AggregateStore
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import kotlinx.coroutines.flow.FlowCollector

class AggregateStage(
    val store: AggregateStore,
) {
    suspend fun apply(
        input: DataFlowStageIO,
        outputFlow: FlowCollector<DataFlowStageIO>,
    ) {
        val key = input.raw!!.stream.mappedDescriptor
        val rec = input.munged!!

        store.acceptFor(key, rec)

        var next = store.removeNextComplete(rec.emittedAtMs)

        while (next != null) {
            outputFlow.emit(
                DataFlowStageIO(
                    aggregate = next.value,
                    partitionHistogram = next.partitionHistogram,
                )
            )
            next = store.removeNextComplete(rec.emittedAtMs)
        }
    }
}
