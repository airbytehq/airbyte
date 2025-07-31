package io.airbyte.cdk.load.lifecycle.steps

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.transform

@Singleton
class RecordAccumulator(
    val openLoaders: MutableMap<DestinationStream.Descriptor, DirectLoader>,
    // TODO: redo the directLoader and factory (No generic)
    val directLoaderFactory: DirectLoaderFactory<DirectLoader>) {

    data class AccumulatorState(
        val recordPerStreamDescriptor: MutableMap<DestinationStream.Descriptor, Int> = mutableMapOf()
    )

    // TODO: Inject
    private val maxNumConcurrentKeys: Int = 42
    private val accumulatorState = AccumulatorState()

    /**
     * Accumulate records in a Loader, once all the record have been accumulated it return the StreamDescriptor to flush
     */
    fun accumulateRecord(/*recordFlow: Flow<TransformDataStep.MungedRecordWrapper>*/) {
        // recordFlow.transform { mungedRecord ->
        //     val recordPerStreamDescriptor = accumulatorState.recordPerStreamDescriptor
        //     // TODO: Check num of open loader, flush if needed. Return the COMPLETED stream descriptor if needed or the forced flush one
        //     if (recordPerStreamDescriptor.containsKey(mungedRecord.stream.mappedDescriptor) &&
        //         recordPerStreamDescriptor.size >= maxNumConcurrentKeys) {
        //         val biggestDirectLoader = recordPerStreamDescriptor.maxBy { it.value }
        //         // TODO: In the flush we need to block
        //         emit(biggestDirectLoader.key)
        //         recordPerStreamDescriptor.remove(biggestDirectLoader.key)
        //         // TODO: Part or new interface
        //         val newDirectLoader = directLoaderFactory.create(mungedRecord.stream.mappedDescriptor, 0)
        //         openLoaders.put(mungedRecord.stream.mappedDescriptor, newDirectLoader)
        //     }
        //     if (openLoaders.containsKey(mungedRecord.stream.mappedDescriptor)) {
        //         // TODO: new interface
        //         val result = openLoaders[mungedRecord.stream.mappedDescriptor]!!.accept(mungedRecord.mungedRecord)
        //         if (result == DirectLoader.Complete) {
        //             // emit()
        //         }
        //     }
        // }
    }
}
