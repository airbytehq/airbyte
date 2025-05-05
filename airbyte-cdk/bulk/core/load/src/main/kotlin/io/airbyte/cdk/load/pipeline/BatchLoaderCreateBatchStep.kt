package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.BatchLoadStrategy
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong

@Singleton
@Requires(bean = BatchLoadStrategy::class)
class BatchLoaderCreateBatchStep<K: WithStream>(
    val factory: LoadPipelineStepTaskFactory,
    val loadStrategy: BatchLoadStrategy,
    @Named("pipelineInputQueue") val inputQueue: PartitionedQueue<PipelineEvent<K, DestinationRecordRaw>>,
    val flushStrategy: PipelineFlushStrategy,
    @Named("batchStateUpdateQueue") val batchStateUpdateQueue: ChannelMessageQueue<BatchUpdate>,
): LoadPipelineStep {
    override val numWorkers: Int
        get() = TODO("Not yet implemented")

    private val streamCompletions =
        ConcurrentHashMap<Pair<DestinationStream.Descriptor, String>, AtomicLong>()

    override fun taskForPartition(partition: Int): Task {
        return BatchLoaderCreateBatchTask(
            inputQueue.consume(partition),
            flushStrategy,
            loadStrategy,
            partition,
            batchStateUpdateQueue,
        )
    }
}
