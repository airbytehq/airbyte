/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql;

import io.airbyte.integrations.base.ssh.SshTunnel;

public class SshKeyMSSQLDestinationAcceptanceTest extends SshMSSQLDestinationAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_KEY_AUTH;
  }

}
