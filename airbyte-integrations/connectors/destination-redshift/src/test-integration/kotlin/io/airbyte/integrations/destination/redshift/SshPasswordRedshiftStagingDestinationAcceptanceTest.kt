/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import io.airbyte.cdk.integrations.base.ssh.SshTunnel
import org.junit.jupiter.api.Disabled

/**
 * SshPasswordRedshiftStagingDestinationAcceptanceTest runs basic Redshift Destination Tests using
 * the S3 Staging mechanism for upload of data and "password" authentication for the SSH bastion
 * configuration.
 */
@Disabled
class SshPasswordRedshiftStagingDestinationAcceptanceTest :
    SshRedshiftDestinationBaseAcceptanceTest() {
    override val tunnelMethod: SshTunnel.TunnelMethod
        get() = SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH
}
