/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.aggregate.AggregateStore
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.FlowCollector

@Named("aggregate")
@Singleton
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
