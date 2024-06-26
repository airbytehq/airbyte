/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import io.airbyte.cdk.integrations.base.ssh.SshTunnel
import org.junit.jupiter.api.Disabled

/*
 * SshKeyRedshiftInsertDestinationAcceptanceTest runs basic Redshift Destination Tests using the SQL
 * Insert mechanism for upload of data and "key" authentication for the SSH bastion configuration.
 */
@Disabled
class SshKeyRedshiftS3StagingDestinationAcceptanceTest :
    SshRedshiftDestinationBaseAcceptanceTest() {
    override val tunnelMethod: SshTunnel.TunnelMethod
        get() = SshTunnel.TunnelMethod.SSH_KEY_AUTH
}
