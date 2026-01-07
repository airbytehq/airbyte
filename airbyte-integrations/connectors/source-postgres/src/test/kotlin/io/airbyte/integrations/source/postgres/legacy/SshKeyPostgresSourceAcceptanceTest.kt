package io.airbyte.integrations.source.postgres.legacy

import io.airbyte.cdk.test.fixtures.legacy.SshTunnel


class SshKeyPostgresSourceAcceptanceTest : AbstractSshPostgresSourceAcceptanceTest() {
    override val tunnelMethod: SshTunnel.TunnelMethod
        get() = SshTunnel.TunnelMethod.SSH_KEY_AUTH
}
