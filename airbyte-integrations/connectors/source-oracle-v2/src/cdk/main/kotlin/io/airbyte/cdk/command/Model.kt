/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.time.Duration

/**
 * Connector configuration POJO supertype.
 *
 * This dummy base class is required by Micronaut. Without it, thanks to Java's type erasure, it
 * thinks that the [ConfigurationJsonObjectSupplier] requires a constructor argument of type [Any].
 *
 * Strictly speaking, its subclasses are not really POJOs anymore, but who cares.
 */
abstract class ConfigurationJsonObjectBase

/**
 * Interface that defines a typed connector configuration.
 *
 * Prefer this or its implementations over the corresponding configuration POJOs; i.e.
 * [ConfigurationJsonObjectBase] subclasses.
 */
sealed interface Configuration {

    val realHost: String
    val realPort: Int
    val sshTunnel: SshTunnelMethodConfiguration
    val sshConnectionOptions: SshConnectionOptions

    val workerConcurrency: Int
    val workUnitSoftTimeout: Duration
}

/** Subtype of [Configuration] for sources. */
interface SourceConfiguration : Configuration {

    /** Does READ generate states of type GLOBAL? */
    val global: Boolean

    /**
     * JDBC URL format string with placeholders for the host and port. These are dynamically
     * assigned by SSH tunnel port forwarding, if applicable.
     */
    val jdbcUrlFmt: String

    /** Properties map (with username, password, etc.) passed along to the JDBC driver. */
    val jdbcProperties: Map<String, String>

    /** Ordered set of schemas for the connector to consider. */
    val schemas: Set<String>
}

/** Union type of the state passed as input to a READ for a source connector. */
sealed interface InputState

data object EmptyInputState : InputState

data class GlobalInputState(
    val global: GlobalStateValue,
    val globalStreams: Map<AirbyteStreamNameNamespacePair, StreamStateValue>,
    /** Conceivably, some streams may undergo a full refresh alongside independently of the rest. */
    val nonGlobalStreams: Map<AirbyteStreamNameNamespacePair, StreamStateValue>,
) : InputState

data class StreamInputState(
    val streams: Map<AirbyteStreamNameNamespacePair, StreamStateValue>,
) : InputState

/** State value for a STATE message of type STREAM. */
data class StreamStateValue(
    @JsonProperty("primary_key") val primaryKey: Map<String, String> = mapOf(),
    @JsonProperty("cursors") val cursors: Map<String, String> = mapOf(),
)

/** State value for a STATE message of type GLOBAL. */
data class GlobalStateValue(@JsonProperty("cdc") val cdc: JsonNode)
