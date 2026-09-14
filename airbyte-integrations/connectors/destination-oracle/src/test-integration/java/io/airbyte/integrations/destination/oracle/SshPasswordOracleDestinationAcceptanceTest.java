/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

import io.airbyte.cdk.integrations.base.ssh.SshTunnel;

public class SshPasswordOracleDestinationAcceptanceTest extends SshOracleDestinationAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;
  }

}
