/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.Reserved
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel

sealed interface CheckpointMessageWrapped

data class StreamCheckpointWrapped(
    val stream: DestinationStream.Descriptor,
    val checkpointId: CheckpointId,
    val checkpoint: CheckpointMessage
) : CheckpointMessageWrapped

data class GlobalCheckpointWrapped(
    val streamIndexes: List<Pair<DestinationStream.Descriptor, CheckpointId>>,
    val checkpoint: CheckpointMessage
) : CheckpointMessageWrapped

/**
 * A single-channel queue for checkpoint messages. This is so updating the checkpoint manager never
 * blocks reading from stdin.
 */
// TODO: DI: Move to factory
@Singleton
@Secondary
class CheckpointMessageQueue :
    ChannelMessageQueue<Reserved<CheckpointMessageWrapped>>(Channel(Channel.UNLIMITED))
