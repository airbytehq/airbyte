/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import io.airbyte.cdk.integrations.base.ssh.SshTunnel;

public class SshKeyClickhouseDestinationAcceptanceTest extends SshClickhouseDestinationAcceptanceTest {

  @Override
  public SshTunnel.TunnelMethod getTunnelMethod() {
    return SshTunnel.TunnelMethod.SSH_KEY_AUTH;
  }

}
