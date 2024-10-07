/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.ssh

import kotlin.time.Duration
import kotlin.time.Duration.Companion.ZERO
import kotlin.time.Duration.Companion.milliseconds

/** These can be passed in the connector configuration as additional parameters. */
data class SshConnectionOptions(
    val sessionHeartbeatInterval: Duration,
    val globalHeartbeatInterval: Duration,
    val idleTimeout: Duration,
) {
    companion object {
        fun fromAdditionalProperties(map: Map<String, Any>) =
            SshConnectionOptions(
                when (val millis = map["session_heartbeat_interval"]) {
                    is Long -> millis.milliseconds
                    else -> 1_000.milliseconds
                },
                when (val millis = map["global_heartbeat_interval"]) {
                    is Long -> millis.milliseconds
                    else -> 2_000.milliseconds
                },
                when (val millis = map["idle_timeout"]) {
                    is Long -> millis.milliseconds
                    else -> ZERO
                },
            )
    }
}
