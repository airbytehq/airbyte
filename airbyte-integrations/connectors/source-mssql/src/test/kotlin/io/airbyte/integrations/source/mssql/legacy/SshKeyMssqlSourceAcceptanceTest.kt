/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql.legacy

import io.airbyte.cdk.test.fixtures.legacy.SshTunnel

class SshKeyMssqlSourceAcceptanceTest : AbstractSshMssqlSourceAcceptanceTest() {
    override val tunnelMethod: SshTunnel.TunnelMethod
        get() = SshTunnel.TunnelMethod.SSH_KEY_AUTH
}
