/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteMessage

/** Convenience object for return values in [CliRunner]. */
data class CliRunnable(
    val runnable: Runnable,
    val results: BufferingOutputConsumer,
) {

    /** Decorates the [BufferingOutputConsumer] with a callback, which should return quickly. */
    fun withCallback(nonBlockingFn: (AirbyteMessage) -> Unit): CliRunnable {
        results.callback = nonBlockingFn
        return this
    }

    /** Runs the [Runnable]. */
    fun run(): BufferingOutputConsumer {
        runnable.run()
        return results
    }
}
