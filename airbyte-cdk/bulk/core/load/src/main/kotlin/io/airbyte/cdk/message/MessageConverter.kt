/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.StreamDescriptor
import jakarta.inject.Singleton

/**
 * Converts the internal @[CheckpointMessage] case class to the Protocol state messages required by
 * @[io.airbyte.cdk.output.OutputConsumer]
 */
interface MessageConverter<T, U> {
    fun from(message: T): U
}

@Singleton
class DefaultMessageConverter : MessageConverter<CheckpointMessage, AirbyteMessage> {
    override fun from(message: CheckpointMessage): AirbyteMessage {
        val state =
            when (message) {
                is StreamCheckpoint ->
                    AirbyteStateMessage()
                        .withSourceStats(
                            AirbyteStateStats()
                                .withRecordCount(message.sourceStats.recordCount.toDouble())
                        )
                        .withDestinationStats(
                            message.destinationStats?.let {
                                AirbyteStateStats().withRecordCount(it.recordCount.toDouble())
                            }
                                ?: throw IllegalStateException(
                                    "Destination stats must be provided for DestinationStreamState"
                                )
                        )
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(fromStreamState(message.checkpoint))
                is GlobalCheckpoint ->
                    AirbyteStateMessage()
                        .withSourceStats(
                            AirbyteStateStats()
                                .withRecordCount(message.sourceStats.recordCount.toDouble())
                        )
                        .withDestinationStats(
                            message.destinationStats?.let {
                                AirbyteStateStats().withRecordCount(it.recordCount.toDouble())
                            }
                        )
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                        .withGlobal(
                            AirbyteGlobalState()
                                .withSharedState(message.state)
                                .withStreamStates(message.checkpoints.map { fromStreamState(it) })
                        )
            }
        return AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(state)
    }

    private fun fromStreamState(checkpoint: CheckpointMessage.Checkpoint): AirbyteStreamState {
        return AirbyteStreamState()
            .withStreamDescriptor(
                StreamDescriptor()
                    .withNamespace(checkpoint.stream.descriptor.namespace)
                    .withName(checkpoint.stream.descriptor.name)
            )
            .withStreamState(checkpoint.state)
    }
}
