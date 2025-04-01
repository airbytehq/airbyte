/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.CheckpointId

/** Used internally by the CDK to pass messages between steps in the loader pipeline. */
sealed interface PipelineEvent<K : WithStream, T>

/**
 * A message that contains a keyed payload. The key is used to manage the state of the payload's
 * corresponding [io.airbyte.cdk.load.pipeline.BatchAccumulator]. [checkpointCounts] is used by the
 * CDK to perform state message bookkeeping. [postProcessingCallback] is for releasing resources
 * associated with the message.
 */
class PipelineMessage<K : WithStream, T>(
    val checkpointCounts: Map<CheckpointId, Long>,
    val key: K,
    val value: T,
    val postProcessingCallback: suspend () -> Unit = {},
) : PipelineEvent<K, T>

/** Broadcast at end-of-stream to all partitions to signal that the stream has ended. */
class PipelineEndOfStream<K : WithStream, T>(val stream: DestinationStream.Descriptor) :
    PipelineEvent<K, T>
