package io.airbyte.integrations.source.postgres.legacy

import io.airbyte.cdk.test.fixtures.legacy.SshTunnel

class SshPasswordPostgresSourceAcceptanceTest : AbstractSshPostgresSourceAcceptanceTest() {
    override val tunnelMethod: SshTunnel.TunnelMethod
        get() = SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH
}
