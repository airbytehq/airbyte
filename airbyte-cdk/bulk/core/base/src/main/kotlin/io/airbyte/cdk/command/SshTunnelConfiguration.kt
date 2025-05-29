/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration

interface SshTunnelConfiguration {
    val realHost: String
    val realPort: Int
    val sshTunnel: SshTunnelMethodConfiguration
    val sshConnectionOptions: SshConnectionOptions
}
