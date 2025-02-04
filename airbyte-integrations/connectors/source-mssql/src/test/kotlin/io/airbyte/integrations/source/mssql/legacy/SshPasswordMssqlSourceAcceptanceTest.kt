/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql.legacy

import io.airbyte.cdk.test.fixtures.legacy.SshTunnel
import org.junit.jupiter.api.Test

class SshPasswordMssqlSourceAcceptanceTest : AbstractSshMssqlSourceAcceptanceTest() {
    override val tunnelMethod: SshTunnel.TunnelMethod
        get() = SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH
    @Test
    override fun testGetSpec() {
        super.testGetSpec()
    }
}
