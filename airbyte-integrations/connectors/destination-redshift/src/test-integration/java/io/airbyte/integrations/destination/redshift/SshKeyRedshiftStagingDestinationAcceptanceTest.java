/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import io.airbyte.cdk.integrations.base.ssh.SshTunnel.TunnelMethod;
import org.junit.jupiter.api.Disabled;

/*
 * SshKeyRedshiftInsertDestinationAcceptanceTest runs basic Redshift Destination Tests using the SQL
 * Insert mechanism for upload of data and "key" authentication for the SSH bastion configuration.
 */
@Disabled
public class SshKeyRedshiftStagingDestinationAcceptanceTest extends SshRedshiftDestinationBaseAcceptanceTest {

  @Override
  public TunnelMethod getTunnelMethod() {
    return TunnelMethod.SSH_KEY_AUTH;
  }
}
