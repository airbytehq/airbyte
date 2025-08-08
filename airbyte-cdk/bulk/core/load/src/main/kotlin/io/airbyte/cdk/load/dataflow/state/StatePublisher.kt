/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.output.OutputConsumer
import jakarta.inject.Singleton

@Singleton
class StatePublisher(
    private val consumer: OutputConsumer,
) {
    fun publish(msg: CheckpointMessage) {
        consumer.accept(msg.asProtocolMessage())
    }
}
