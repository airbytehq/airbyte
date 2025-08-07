/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentSkipListMap

@Singleton
class StateStore {
    val states = ConcurrentSkipListMap<StateKey, CheckpointMessage>()

    fun accept(key: StateKey, msg: CheckpointMessage) {
        states[key] = msg
    }

    fun remove(key: StateKey): CheckpointMessage = states.remove(key)!!
}
