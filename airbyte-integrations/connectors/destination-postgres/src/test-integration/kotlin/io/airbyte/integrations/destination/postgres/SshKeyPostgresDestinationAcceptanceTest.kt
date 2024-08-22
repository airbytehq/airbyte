/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import io.airbyte.cdk.integrations.base.ssh.SshTunnel
import org.junit.jupiter.api.Disabled

@Disabled("Disabled after DV2 migration. Re-enable with fixtures updated to DV2.")
class SshKeyPostgresDestinationAcceptanceTest : SshPostgresDestinationAcceptanceTest() {
    override val tunnelMethod: SshTunnel.TunnelMethod
        get() = SshTunnel.TunnelMethod.SSH_KEY_AUTH
}
