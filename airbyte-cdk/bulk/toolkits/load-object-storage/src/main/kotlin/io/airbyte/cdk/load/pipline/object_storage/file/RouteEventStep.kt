/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.factory.object_storage.IsFileTransferCondition
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.Task
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow

@Singleton
@Requires(condition = IsFileTransferCondition::class)
class RouteEventStep(
    private val catalog: DestinationCatalog,
    @Named("dataChannelInputFlows")
    private val inputFlows: Array<Flow<PipelineEvent<StreamKey, DestinationRecordRaw>>>,
    @Named("fileQueue")
    private val fileQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    @Named("recordQueue")
    private val recordQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
) : LoadPipelineStep {
    override val numWorkers: Int = 1

    override fun taskForPartition(partition: Int): Task =
        RouteEventTask(
            catalog,
            inputFlows[0],
            fileQueue,
            recordQueue,
            partition,
        )
}
