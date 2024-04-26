/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import java.time.Duration

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

    /** Are resumable backfills preferred to non-resumable backfills? */
    val resumablePreferred: Boolean

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
