/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.CheckpointId

/** Used internally by the CDK to pass messages between steps in the loader pipeline. */
sealed interface PipelineEvent<K : WithStream, T>

class PipelineMessage<K : WithStream, T>(
    val checkpointCounts: Map<CheckpointId, Long>,
    val key: K,
    val value: T
) : PipelineEvent<K, T>

/**
 * We send the end message on the stream and not the key, because there's no way to partition an
 * empty message.
 */
class PipelineEndOfStream<K : WithStream, T>(val stream: DestinationStream.Descriptor) :
    PipelineEvent<K, T>
