/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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
        val emittedAtMs =
            if (input.parsedArrowBatch != null) {
                val batch = input.parsedArrowBatch!!
                store.acceptFor(input.arrowBatch!!.stream.mappedDescriptor, batch)
                batch.emittedAtMs
            } else {
                val record = input.munged!!
                store.acceptFor(input.raw!!.stream.mappedDescriptor, record)
                record.emittedAtMs
            }

        var next = store.removeNextComplete(emittedAtMs)

        while (next != null) {
            next.value.onPublish()
            outputFlow.emit(
                DataFlowStageIO(
                    aggregate = next.value,
                    partitionCountsHistogram = next.partitionCountsHistogram,
                    partitionBytesHistogram = next.partitionBytesHistogram,
                    mappedDesc = next.key,
                )
            )
            next = store.removeNextComplete(emittedAtMs)
        }
    }
}
