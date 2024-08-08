/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
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
interface Configuration {
    val realHost: String
    val realPort: Int
    val sshTunnel: SshTunnelMethodConfiguration
    val sshConnectionOptions: SshConnectionOptions

    val maxConcurrency: Int
    val resourceAcquisitionHeartbeat: Duration
}
