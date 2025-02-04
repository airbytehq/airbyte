/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.write.DirectLoader
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton

/**
 * Used internally by the CDK to implement the DirectLoader.
 *
 * Creates a single pipeline step reading from a (possibly partitioned) record stream. Batch updates
 * are written to the batchStateUpdateQueue whenever the loader returns
 */
@Singleton
class DirectLoadPipeline(
    val pipelineStep: DirectLoadPipelineStep<*>
) : LoadPipeline(listOf(pipelineStep))
