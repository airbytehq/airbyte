/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import io.airbyte.cdk.integrations.base.ssh.SshTunnel
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider
import org.junit.jupiter.api.Disabled

@Disabled("Disabled after DV2 migration. Re-enable with fixtures updated to DV2.")
class SshPasswordPostgresDestinationAcceptanceTest : SshPostgresDestinationAcceptanceTest() {
    override val tunnelMethod: SshTunnel.TunnelMethod
        get() = SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH

    @Disabled(
        "sshpass tunnel is not working with DBT container. https://github.com/airbytehq/airbyte/issues/33547"
    )
    @Throws(Exception::class)
    override fun testIncrementalDedupeSync() {
        super.testIncrementalDedupeSync()
    }

    @Disabled(
        "sshpass tunnel is not working with DBT container. https://github.com/airbytehq/airbyte/issues/33547"
    )
    @Throws(Exception::class)
    override fun testDataTypeTestWithNormalization(
        messagesFilename: String,
        catalogFilename: String,
        testCompatibility: DataTypeTestArgumentProvider.TestCompatibility
    ) {
        super.testDataTypeTestWithNormalization(
            messagesFilename,
            catalogFilename,
            testCompatibility
        )
    }

    @Disabled(
        "sshpass tunnel is not working with DBT container. https://github.com/airbytehq/airbyte/issues/33547"
    )
    @Throws(Exception::class)
    override fun testSyncWithNormalization(messagesFilename: String, catalogFilename: String) {
        super.testSyncWithNormalization(messagesFilename, catalogFilename)
    }

    @Disabled(
        "sshpass tunnel is not working with DBT container. https://github.com/airbytehq/airbyte/issues/33547"
    )
    @Throws(Exception::class)
    override fun testCustomDbtTransformations() {
        super.testCustomDbtTransformations()
    } // TODO: Although testCustomDbtTransformationsFailure is passing, the failure is for wrong
    // reasons.
    // See disabled tests.
}
